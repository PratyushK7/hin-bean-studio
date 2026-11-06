"""See what the agent is doing, and how far along a video is.

parse(line, job)  turns one line of Claude Code's `--output-format stream-json` into readable lines for the log, and keeps
                  job["activity"] (the latest step) and job["steps"] (how many) up to date.
make_progress()   works out a percentage and the current stage from the FILES a video has produced so far, so the bar is
                  honest (it only moves when something real exists), and works the same whether the agent runs in the
                  background or in its own window.
"""
import json, os, time
from pathlib import Path

import store

COMMANDS = [("build.py new", "Creating the project"), ("build.py voice", "Recording the voiceover and timing every word"),
            ("build.py check", "Checking the shots"), ("build.py stills", "Rendering stills to check the pictures"),
            ("build.py video", "Rendering the video"), ("build.py thumb", "Rendering the thumbnail"), ("build.py sheet", "Making the contact sheet")]


def describe(name, inp):
    """one short human line for a tool call"""
    base = lambda k: os.path.basename(str(inp.get(k, ""))) or "a file"
    if name == "Read": return f"Reading {base('file_path')}"
    if name == "Write": return f"Writing {base('file_path')}"
    if name in ("Edit", "NotebookEdit"): return f"Editing {base('file_path')}"
    if name in ("Bash", "PowerShell"):
        cmd = str(inp.get("command", "")).replace("\n", " ").strip()
        for key, text in COMMANDS:
            if key in cmd: return text
        if "yt_dlp" in cmd or "yt-dlp" in cmd: return "Looking up videos on YouTube"
        return "Running: " + (cmd[:110] + ("…" if len(cmd) > 110 else ""))
    if name == "WebSearch": return f"Searching the web: {str(inp.get('query', ''))[:90]}"
    if name == "WebFetch": return f"Reading a web page: {str(inp.get('url', ''))[:80]}"
    if name in ("Glob", "Grep"): return f"Searching the project for {str(inp.get('pattern', ''))[:60]}"
    if name == "Skill": return f"Using the {inp.get('skill', '')} skill"
    if name in ("Task", "Agent"): return "Handing a part to a helper agent"
    return name


def parse(raw, job):
    """-> list of log lines for one raw line of stream-json (non-JSON lines pass through untouched)"""
    raw = raw.strip()
    if not raw: return []
    try: ev = json.loads(raw)
    except ValueError: return [raw]
    kind, out = ev.get("type"), []
    if kind == "system" and ev.get("subtype") == "init":
        out.append(f"▸ Agent started ({ev.get('model', 'model')})")
    elif kind == "assistant":
        for b in (ev.get("message") or {}).get("content", []) or []:
            if not isinstance(b, dict): continue
            if b.get("type") == "tool_use":
                text = describe(b.get("name", ""), b.get("input") or {})
                job["activity"], job["steps"] = text, job.get("steps", 0) + 1
                out.append("▸ " + text)
            elif b.get("type") == "text" and b.get("text", "").strip():
                out.append("💬 " + " ".join(b["text"].split())[:300])
    elif kind == "user":
        c = (ev.get("message") or {}).get("content")
        for b in (c if isinstance(c, list) else []):
            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                out.append("✗ " + " ".join(str(b.get("content", "")).split())[:200])
    elif kind == "result":
        job["activity"] = "Finished"
        secs = round((ev.get("duration_ms") or 0) / 1000)
        job.update(cost=ev.get("total_cost_usd"), turns=ev.get("num_turns"), usage=ev.get("usage") or {})
        cost = f", about ${ev['total_cost_usd']:.2f} at API prices" if isinstance(ev.get("total_cost_usd"), (int, float)) else ""
        out.append(f"{'✗' if ev.get('is_error') else '✓'} {'Failed' if ev.get('is_error') else 'Finished'} after {secs // 60} min {secs % 60} s and {ev.get('num_turns', '?')} turns{cost}")
        if ev.get("result"): out.append(str(ev["result"]).strip())
    return out


# ---------- progress from the files ----------
def _words(p):
    from_json = store.read(p / "script.json", [])
    return len(" ".join(from_json).split()) if isinstance(from_json, list) else 0


def _real(p, rel, size):
    f = p / rel
    return f.exists() and f.stat().st_size > size


def _chapter_files(p):
    """0..1: how many chapter shot files exist out of the chapters planned in chapters.json (a stage can be part done)"""
    planned = store.read(p / "chapters.json", [])
    have = len(list((p / "web" / "shots").glob("*.js"))) if (p / "web" / "shots").is_dir() else 0
    return min(1.0, have / len(planned)) if isinstance(planned, list) and planned else (1.0 if have else 0.0)


STAGES = {
    "short": [("Writing the script", 10, lambda p, n: _words(p) > 20),
              ("Recording the voiceover", 12, lambda p, n: (p / "audio" / "words.json").exists()),
              ("Drawing the characters and shots", 28, lambda p, n: _real(p, "web/shots.js", 800) and _real(p, "web/cast.js", 300)),
              ("Checking the pictures", 8, lambda p, n: (p / "stills").is_dir() and any((p / "stills").iterdir())),
              ("Rendering the video", 22, lambda p, n: (p / f"{n}.mp4").exists()),
              ("Adding captions", 4, lambda p, n: (p / f"{n}.srt").exists()),
              ("Making the thumbnail", 8, lambda p, n: (p / f"{n}-thumbnail.png").exists()),
              ("Writing the upload sheet", 8, lambda p, n: (p / f"{n}-youtube.txt").exists())],
    "long": [("Writing the script", 8, lambda p, n: _words(p) > 60),
             ("Recording the voiceover", 7, lambda p, n: (p / "audio" / "words.json").exists()),
             ("Checking the sources", 10, lambda p, n: (p / f"{n}-sources.md").exists()),
             ("Timing the chapters", 4, lambda p, n: (p / f"{n}-chapters.txt").exists()),
             ("Drawing the chapters", 28, lambda p, n: _chapter_files(p)),
             ("Checking the pictures", 3, lambda p, n: (p / "stills").is_dir() and any((p / "stills").iterdir())),
             ("Rendering the video", 25, lambda p, n: (p / f"{n}.mp4").exists()),
             ("Adding captions", 3, lambda p, n: (p / f"{n}.srt").exists()),
             ("Writing the upload sheet", 6, lambda p, n: (p / f"{n}-youtube.txt").exists())],
}


def make_progress(project_dir, kind="short"):
    """{pct, stage, done:[...]}: what exists so far, and what the agent is on now"""
    p = Path(project_dir)
    stages = STAGES.get(kind, STAGES["short"])
    vals = []
    for label, weight, test in stages:
        try: vals.append(float(p.is_dir() and test(p, p.name)))        # True/False, or a fraction for a stage that is part done
        except OSError: vals.append(0.0)
    done, pct, current = [], 0.0, None
    for i, (label, weight, _) in enumerate(stages):
        v = vals[i]
        if v < 1 and any(x >= 1 for x in vals[i + 1:]): v = 1.0       # a stage the agent skipped (say, no stills) counts once something after it exists
        pct += weight * v
        if v >= 1: done.append(label)
        elif current is None: current = label + (f" ({round(v * 100)}%)" if 0 < v < 1 else "")
    return {"pct": min(100, round(pct)), "stage": current or "All done", "done": done}


def clock(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m} min {s:02d} s" if m else f"{s} s"
