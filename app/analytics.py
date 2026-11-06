"""Analytics for Bean Studio: numbers pulled from YouTube by the server, and the agent's report on them.

register(app, ROOT, cfg, start_job) adds /api/analytics*, /api/reports*.
Data lives in data/analytics.json, reports in reports/analysis-<date>.md (both tracked in git, both private).
Only slot, type, project, notes and the Studio-only "viewed %" / drop note are editable by hand; everything else is replaced by each sync.
"""
import datetime as dt, json, re, threading, time

from flask import abort, jsonify, request

import store

FIELDS = ["id", "project", "title", "posted", "duration_s", "slot", "type", "checked", "detail_checked", "views", "engaged_pct", "viewed_pct",
          "avg_pct", "avd_s", "likes", "comments", "shares", "subs", "drop_s", "retention", "drop_note", "geo", "notes"]
EDITABLE = ("project", "slot", "type", "notes", "viewed_pct", "drop_note")


def num(v):
    if v in (None, ""): return None
    try:
        return float(str(v).replace(",", "").replace("%", "").strip())
    except ValueError:
        return None


def summarize(rows):
    """per-slot and per-type averages, with the sample size next to each"""
    def agg(key):
        groups = {}
        for r in rows:
            if r.get("views") is None or not r.get(key): continue
            groups.setdefault(r[key], []).append(r)
        out = []
        for k, rs in groups.items():
            def avg(f):
                vals = [x[f] for x in rs if x.get(f) is not None]
                return round(sum(vals) / len(vals), 1) if vals else None
            out.append({key: k, "videos": len(rs), "avg_views": avg("views"), "avg_engaged_pct": avg("engaged_pct"),
                        "avg_viewed_pct": avg("viewed_pct"), "avg_pct_watched": avg("avg_pct"), "avg_subs": avg("subs")})
        return sorted(out, key=lambda x: -(x["avg_views"] or 0))
    return {"by_slot": agg("slot"), "by_type": agg("type")}


def apply_edits(rows, current):
    """copy the hand-set fields of `current` onto `rows` (matched by id, else title), so a sync that took a minute
    never overwrites something you changed while it ran"""
    by_id = {r.get("id"): r for r in current if r.get("id")}
    by_title = {(r.get("title") or "").lower(): r for r in current}
    for r in rows:
        src = by_id.get(r.get("id")) or by_title.get((r.get("title") or "").lower())
        if src:
            for k in EDITABLE:
                if src.get(k) not in (None, ""): r[k] = src[k]
    return rows


def register(app, ROOT, cfg, start_job):
    DATA, REPORTS = ROOT / "data", ROOT / "reports"
    FILE, META = DATA / "analytics.json", DATA / "analytics-meta.json"
    load = lambda: store.read(FILE, [])
    state = {"syncing": False, "error": None, "last_sync": None, "info": None, **(store.read(META, {}) or {})}
    state.update(syncing=False, error=None)
    sync_lock = threading.Lock()

    def do_sync():
        """pull everything from YouTube; keeps the slot/type/project/notes you set by hand"""
        import ytdata, ytstate
        if not sync_lock.acquire(blocking=False):
            return state["error"] is None                 # one is already running
        state["syncing"] = True
        try:
            fresh = ytstate.STATE["videos"] if ytstate.STATE["videos"] and time.time() - ytstate.STATE["at"] < 600 else None
            rows, info = ytdata.sync(ROOT, cfg(), load(), videos=fresh)
            with store.lock_for(FILE):
                store.write(FILE, apply_edits(rows, load()))
            state.update(error=None, last_sync=dt.datetime.now().isoformat(timespec="seconds"), info=info)
        except ytdata.NotConnected:
            state["error"] = "not connected"
        except Exception as e:
            state["error"] = ytdata.friendly(e)
        finally:
            state["syncing"] = False
            store.write(META, {"last_sync": state["last_sync"], "info": state["info"]})
            sync_lock.release()
        return state["error"] is None

    def auto_sync():
        import ytdata
        time.sleep(15)
        while True:
            hours = float(cfg().get("analytics_sync_hours", 6))
            last = dt.datetime.fromisoformat(state["last_sync"]) if state.get("last_sync") else None
            if hours > 0 and (last is None or (dt.datetime.now() - last).total_seconds() > hours * 3600) and ytdata.connected(ROOT)[0]:
                do_sync()
            time.sleep(300)
    threading.Thread(target=auto_sync, daemon=True).start()

    def status():
        import ytdata
        ok, missing = ytdata.connected(ROOT)
        return {"connected": ok, "missing": missing, "syncing": state["syncing"], "error": state["error"],
                "last_sync": state["last_sync"], "info": state["info"], "auto_hours": cfg().get("analytics_sync_hours", 6)}

    @app.post("/api/analytics/sync")
    def analytics_sync():
        ok = do_sync()
        rows = load()
        return jsonify(ok=ok, rows=rows, summary=summarize(rows), status=status())

    @app.get("/api/analytics")
    def analytics_get():
        rows = load()
        return jsonify(rows=rows, summary=summarize(rows), status=status())

    @app.put("/api/analytics")
    def analytics_put():
        """saves only the fields you can edit, merged into the CURRENT data, so a sync that ran since you opened the tab keeps its numbers"""
        incoming = (request.get_json(silent=True) or {}).get("rows")
        if not isinstance(incoming, list): abort(400, "rows must be a list")
        with store.lock_for(FILE):
            rows = load()
            by_id = {r.get("id"): r for r in rows if r.get("id")}
            by_title = {(r.get("title") or "").lower(): r for r in rows}
            changed = 0
            for inc in incoming:
                tgt = by_id.get(inc.get("id")) or by_title.get((inc.get("title") or "").lower())
                if not tgt: continue
                for k in EDITABLE:
                    if k in inc:
                        v = num(inc[k]) if k == "viewed_pct" else (inc[k] or None)
                        if tgt.get(k) != v: tgt[k] = v; changed += 1
            if changed: store.write(FILE, rows)
        return jsonify(ok=True, changed=changed)

    @app.post("/api/analytics/analyze")
    def analytics_analyze():
        rows = [r for r in load() if r.get("views") is not None]
        if len(rows) < 2: abort(400, "no numbers yet: connect YouTube and sync first (at least 2 videos needed)")
        question = str((request.get_json(silent=True) or {}).get("question") or "").strip()[:500]
        REPORTS.mkdir(exist_ok=True)
        out = REPORTS / f"analysis-{dt.datetime.now():%Y-%m-%d-%H%M}.md"
        c = cfg()
        prompt = f"""You are the analyst for the YouTube channel "{c['channel']}" (serious Hindi-language explainers using documentary storytelling, data visualization and custom code-generated animation; slot A posts at {c['slots'].get('A')} IST, slot B at {c['slots'].get('B')} IST).
Analyze the channel's numbers and write a report to {out} (Markdown). Read {FILE} (every row, pulled from YouTube by the server: video type, slot, views, engaged_pct, average % watched, subs, top countries, the retention curve as [second, % still watching] pairs, and drop_s = the second with the biggest loss after the first 10%), {c['planner']} (the Schedule and Types tabs) and, for any video you want to explain, its folder under {c['projects_dir']} (script.json and <name>-youtube.txt). Also read .claude/skills/hindi-explainer/references/channel-voice.md for the channel voice.

Summary the app computed (a cross-check; recompute anything that looks off):
{json.dumps(summarize(rows), indent=1)}
{('The user also asks: ' + question) if question else ''}

Rules:
- Never invent a number. Quote only what is in the data, and write "n = X" next to any average.
- Be honest about sample size: with fewer than about 5 videos in a group, or under about 1,000 views per video, call a pattern a hint, not a conclusion. Do not recommend big changes on thin data.
- For Shorts the useful signals are engaged_pct (engaged views / views, a proxy for the hook; YouTube's own "viewed vs swiped away" is not in the API, so viewed_pct is only filled if the user typed it from Studio), average % watched (retention and loop) and subs per 1,000 views. Raw views mostly reflect distribution.
- Use drop_s and the retention curve to say which line or shot lost people: read the project's web/words.js or script.json to see what was said at that second, and say what to change in the next script.
- Slot and type were inferred from publish time and the planner; if one looks wrong for a row, say so rather than trusting it.

- Read the retention curve the way the yt-retention skill (~/.claude/skills/yt-retention/SKILL.md) does: a HOOK LEAK (what is lost in the first 30 seconds; under 25% is healthy), CLIFFS (single steep drops, tied to what was being said at that second) and a SLIDE (the steady bleed across the middle: pacing, fixed by cutting). Name the single biggest leak and one change for it; if the hook leak is healthy and the slide is flat, say the video is fine and the problem is packaging (yt-package).

Report structure:
# Analysis <date>
## What the data says (5 bullets max, each with the number)
## What is probably noise
## Slot A vs slot B (and India vs US if the geo column has data)
## Video types: keep / double / drop
## Hook and retention: fixes for the next scripts
## Decisions (max 3; each has the change, the number that justifies it, and how to test it)
## Next checkpoint (what to collect and when)
Only write the report. Do not edit the planner, the skills or any video. Finish by printing the Decisions section."""
        j = start_job("analyze · analytics", list(c["agent_command"]) + [prompt], c["agent_cwd"])
        return jsonify(id=j["id"], label=j["label"], report=out.name)

    @app.get("/api/reports")
    def reports_list():
        REPORTS.mkdir(exist_ok=True)
        return jsonify([{"name": f.name, "modified": f.stat().st_mtime} for f in sorted(REPORTS.glob("*.md"), key=lambda f: -f.stat().st_mtime)])

    @app.get("/api/reports/<name>")
    def report_get(name):
        if not re.match(r"^[\w.-]+\.md$", name): abort(400)
        f = REPORTS / name
        if not f.exists(): abort(404, "not written yet")
        return jsonify(name=name, text=f.read_text(encoding="utf-8"))
