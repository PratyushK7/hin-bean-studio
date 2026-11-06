"""Hindi Explainer Studio: a local production dashboard for serious Hindi explainers.

    start.bat                 (or)    .venv\\Scripts\\python app\\server.py

Serves http://127.0.0.1:<port> (localhost only). Everything it does runs a command from config.json on this
machine: the configured renderer, YouTube uploader and Claude Code agent.
"""
import datetime as dt, json, os, re, shutil, stat, subprocess, sys, threading, time, uuid, webbrowser
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask, jsonify, request, send_from_directory, abort

import agentlog, planner, store

APP = Path(__file__).resolve().parent
ROOT = APP.parent                                      # the youtube folder
CONFIG = ROOT / "config.json"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
DEFAULTS = {
    "port": 5173,
    "open_browser": True,
    "projects_dir": str(ROOT / "projects"),
    "planner": str(ROOT / "data" / "planner.xlsx"),
    "python": sys.executable,   # the .venv python: has the uploader libs; build.py re-runs itself under the kit
    "engine": str(Path.home() / ".claude" / "skills" / "line-boil" / "engine" / "build.py"),
    "uploader": str(ROOT / "tools" / "yt_upload.py"),
    "agent_command": ["claude", "-p", "--permission-mode", "acceptEdits"],
    "agent_cwd": str(ROOT),
    "slots": {"A": "19:00", "B": "12:00", "Long": "20:30"},
    "channel": "Hindi Explainer Studio",
    "hide_projects": [],   # folders in projects_dir that aren't videos
    "analytics_sync_hours": 6,          # 0 = only when you press Sync now
    "topic_category": "serious Hindi-language explainers and documentary storytelling across science, technology, history, economics, psychology, geopolitics and society",
    "topic_channels": [
        # documentary explainers and research channels
        "TEDEd", "kurzgesagt", "MinuteEarth", "AsapSCIENCE", "SciShow", "Veritasium", "Vox", "JohnnyHarris", "Wendoverproductions", "RealLifeLore", "EconomicsExplained", "ColdFusion", "Fireship", "ThinkSchool", "Soch by Mohak", "Dhruv Rathee", "StudyIQ IAS", "GetsetflySCIENCE", "Nitish Rajput", "LifeNoggin", "WhatIfScienceShow", "TheOdd1sOut", "JaidenAnimations", "OverSimplified", "Psych2go", "ThoughtCafe", "PrimerBlobs", "ZackDFilms", "RyanGeorge", "SciShowKids",
        # science and how things work
        "veritasium", "Vsauce", "Vsauce2", "Vsauce3", "Numberphile", "3blue1brown", "minutephysics", "SmarterEveryDay", "SteveMould", "NileRed", "TheActionLab", "ElectroBOOM", "PBSSpaceTime", "ArvinAsh", "DomainOfScience", "MarkRober", "PracticalEngineering", "colinfurze", "CrashCourse", "SciShowPsych", "SciShowSpace",
        # health and the body
        "DoctorMike", "ChubbyEmu", "MedCram", "HealthyGamerGG", "BrainCraft", "DrBecky",
        # money and business
        "EconomicsExplained", "PolyMatter", "Wendoverproductions", "BenFelixCSI", "HowMoneyWorks", "TheB1M", "FinanceWithSharan", "CARachanaRanade", "warikoo",
        # history, world and culture
        "CGPGrey", "Vox", "johnnyharris", "RealLifeLore", "HistoriaCivilis", "extrahistory", "TheInfographicsShow", "Lemmino", "MentalFloss", "NowThis",
        # tech, productivity and learning
        "ColdFusion", "Fireship", "Computerphile", "TwoMinutePapers", "Mrwhosetheboss", "Techquickie", "MKBHD", "ThomasFrank", "CleoAbram", "Nerdwriter1", "TomScottGo", "LegalEagle", "dhruvrathee", "DailyDoseOfInternet",
    ],
    "options_model": "",                  # model that adapts outliers into 5 ideas (empty = the session default)
    "thumbnail_model": "",                # empty = the session default
    "thumbnail_model_short": "",          # empty = the session default
    "video_model": "",                  # one model for every video; empty = the session default
    "video_model_short": "",          # empty = the session default
    "video_model_long": "",           # empty = the session default
    "agent_window": False,              # True: every video the agent makes opens in its own visible Claude window
}
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.json.sort_keys = False        # keep the order we build (the checklist chips follow the order of the keys)


# ---------- settings: only your changes live in config.json, so new defaults always reach you ----------
_cfg = {"stamp": "unset", "val": None, "problem": None}

def cfg():
    try: stamp = CONFIG.stat().st_mtime
    except OSError: stamp = None
    if _cfg["val"] is None or _cfg["stamp"] != stamp:
        c, problem = dict(DEFAULTS), None
        if stamp is not None:
            try:
                user = json.loads(CONFIG.read_text(encoding="utf-8"))
                if isinstance(user, dict): c.update(user)
                else: problem = "config.json is not a JSON object; using the defaults"
            except Exception:
                problem = "config.json is not valid JSON; using the defaults until it is fixed"
        _cfg.update(stamp=stamp, val=c, problem=problem)
    return dict(_cfg["val"])

def validate_config(new):
    if not isinstance(new, dict): return ["settings must be a JSON object { ... }"]
    kinds = {"port": int, "open_browser": bool, "projects_dir": str, "planner": str, "python": str, "engine": str, "uploader": str,
             "agent_command": list, "agent_cwd": str, "slots": dict, "channel": str, "hide_projects": list,
             "analytics_sync_hours": (int, float), "topic_category": str, "topic_channels": list, "options_model": str, "video_model": str, "video_model_short": str, "video_model_long": str, "thumbnail_model": str, "thumbnail_model_short": str}
    errs = [f'"{k}" has the wrong type' for k, t in kinds.items() if k in new and (not isinstance(new[k], t) or (t is not bool and isinstance(new[k], bool)))]
    if errs: return errs
    if "agent_command" in new and (not new["agent_command"] or not all(isinstance(x, str) for x in new["agent_command"])):
        errs.append('"agent_command" must be a non-empty list of strings')
    if "slots" in new and not all(isinstance(k, str) and isinstance(v, str) and HHMM.match(v) for k, v in new["slots"].items()):
        errs.append('"slots" must look like {"A": "12:00"} with 24-hour HH:MM times')
    if "topic_channels" in new and not all(isinstance(x, str) and x.strip() for x in new["topic_channels"]):
        errs.append('"topic_channels" must be a list of channel handles')
    if "port" in new and not 1024 <= new["port"] <= 65535: errs.append('"port" must be between 1024 and 65535')
    return errs


# ---------- only this machine may talk to the studio (it can run the agent and post to YouTube) ----------
@app.before_request
def guard():
    if (request.host or "").split(":")[0].lower() not in ("127.0.0.1", "localhost"):
        abort(403, "Hindi Explainer Studio only answers on localhost")            # DNS-rebinding protection
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("Origin")
        if origin and (urlparse(origin).hostname or "") not in ("127.0.0.1", "localhost"):
            abort(403, "cross-site request blocked")

def proj_dir(name):
    if not SLUG.match(name or ""): abort(400, "bad project name")
    p = Path(cfg()["projects_dir"]) / name
    if not p.is_dir(): abort(404, "no such project")
    return p

def body():
    b = request.get_json(silent=True)
    if not isinstance(b, dict): abort(400, "expected a JSON body")
    return b


# ---------- jobs: one background process each, log kept in memory (bounded) ----------
JOBS = {}
MAX_LOG, KEEP_JOBS = 4000, 40

def start_job(label, cmd, cwd, unique=False, parser=None, window=False):
    """runs cmd in the background. unique=True returns the job already running under the same label instead of starting a second.
    parser(line, job) turns raw output lines into log lines (the agent feed); window=True opens the command in its own console window"""
    if unique:
        same = next((j for j in JOBS.values() if j["label"] == label and not j["done"]), None)
        if same: return same
    done = sorted((j for j in JOBS.values() if j["done"]), key=lambda j: j["started"])
    for old in done[:max(0, len(done) - KEEP_JOBS)]: JOBS.pop(old["id"], None)
    jid = uuid.uuid4().hex[:8]
    job = {"id": jid, "label": label, "cmd": cmd, "log": [], "dropped": 0, "done": False, "code": None, "started": time.time()}
    JOBS[jid] = job
    def run():
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", BEAN_PROJECTS_DIR=cfg()["projects_dir"])
        try:
            if window:      # its own console window: you watch (and can answer) the real Claude session
                p = subprocess.Popen(cmd, cwd=cwd, env=env, creationflags=subprocess.CREATE_NEW_CONSOLE)
                job.update(pid=p.pid, window=True, activity="Running in its own Claude window")
                job["log"].append("▸ Opened in its own Claude window. Watch it there; it stays open when it finishes, so close it (or type /exit) afterwards.")
                job["code"] = p.wait()
            else:
                p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                     text=True, encoding="utf-8", errors="replace", env=env)
                job["pid"] = p.pid
                for line in p.stdout:
                    for text in (parser(line, job) if parser else [line.rstrip("\n")]):
                        job["log"].append(text)
                    if len(job["log"]) > MAX_LOG:
                        del job["log"][:500]; job["dropped"] += 500
                job["code"] = p.wait()
        except Exception as e:
            job["log"].append(f"[could not start] {e}"); job["code"] = -1
        job["ended"] = time.time()
        try: record_run(job)
        except Exception: pass
        job["done"] = True
    threading.Thread(target=run, daemon=True).start()
    return job


def record_run(job):
    """keeps a small ledger of agent runs (time, steps, Claude's own cost estimate) so the cost of a video is visible"""
    if job.get("cost") is None: return
    f = ROOT / "data" / "runs.json"
    with store.lock_for(f):
        runs = store.read(f, []) or []
        u = job.get("usage") or {}
        runs.append({"when": time.strftime("%Y-%m-%d %H:%M"), "label": job["label"], "secs": round(job["ended"] - job["started"]), "turns": job.get("turns"),
                     "cost": round(job["cost"], 4), "output_tokens": u.get("output_tokens"), "code": job.get("code")})
        store.write(f, runs[-200:])

@app.get("/api/runs")
def runs():
    rs = store.read(ROOT / "data" / "runs.json", []) or []
    return jsonify(runs=rs[-30:][::-1], total=round(sum(r.get("cost") or 0 for r in rs), 2), count=len(rs))


def start_agent(label, prompt, model=None, mode="plain"):
    """one place that builds the agent's command line. mode: "plain" (output as is), "feed" (live readable steps),
    "window" (its own visible Claude window, interactive)"""
    c = cfg()
    if mode == "window":
        cmd = [x for x in c["agent_command"] if x != "-p"] + (["--model", model] if model else []) + [prompt]   # interactive: no -p
        return start_job(label, cmd, c["agent_cwd"], window=True)
    cmd = list(c["agent_command"]) + (["--model", model] if model else [])
    if mode == "feed": cmd += ["--output-format", "stream-json", "--verbose"]
    return start_job(label, cmd + [prompt], c["agent_cwd"], parser=agentlog.parse if mode == "feed" else None)

def job_view(j):
    v = {k: j[k] for k in ("id", "label", "done", "code", "started")}
    v.update(activity=j.get("activity"), window=bool(j.get("window")), steps=j.get("steps", 0))
    if j["label"].startswith("make · "):         # a video being made: how far along it is, from the files it has produced
        slug = j["label"][7:]
        kind = (store.read(ROOT / "data" / "make" / f"{slug}.json", {}) or {}).get("kind", "short")
        v.update(progress=agentlog.make_progress(Path(cfg()["projects_dir"]) / slug, kind), elapsed=agentlog.clock((time.time() if not j["done"] else j.get("ended", time.time())) - j["started"]), kind=kind)
    return v

@app.get("/api/jobs")
def jobs():
    return jsonify([job_view(j) for j in sorted(JOBS.values(), key=lambda j: -j["started"])][:30])

@app.get("/api/jobs/<jid>")
def job(jid):
    j = JOBS.get(jid) or abort(404, "that job is gone (the studio restarted?)")
    since = int(request.args.get("since", 0))
    return jsonify({"id": jid, "label": j["label"], "done": j["done"], "code": j["code"], "activity": j.get("activity"), "window": bool(j.get("window")),
                    "log": j["log"][max(0, since - j["dropped"]):], "n": j["dropped"] + len(j["log"])})

@app.post("/api/jobs/<jid>/stop")
def stop(jid):
    j = JOBS.get(jid) or abort(404)
    if not j["done"] and j.get("pid"):
        subprocess.run(["taskkill", "/PID", str(j["pid"]), "/T", "/F"], capture_output=True)
    return jsonify(ok=True)


# ---------- projects ----------
def sheet_title(p):
    f = p / f"{p.name}-youtube.txt"
    if not f.exists(): return None
    m = re.search(r"== TITLE ==\s*\n(.+)", f.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None

def summary(p):
    import ytstate
    n = p.name
    has = lambda s: (p / f"{n}{s}").exists()
    upinfo = store.read(p / f"{n}-upload.json")
    script = store.read(p / "script.json", [])
    words = len(" ".join(script).split()) if isinstance(script, list) else 0
    pj = store.read(p / "project.json", {}) or {}
    kind = (store.read(ROOT / "data" / "make" / f"{n}.json", {}) or {}).get("kind") or ("long" if pj.get("format") == "wide" else "short")
    if kind == "long":     # a 16:9 video with chapters and sources, made with the line-boil-wide skill
        steps = {"script": words > 20, "sources": has("-sources.md"), "chapters": has("-chapters.txt"), "video": has(".mp4"), "srt": has(".srt"),
                 "thumbnail": has("-thumbnail.png"), "sheet": has("-youtube.txt"), "uploaded": bool(upinfo)}
    else:
        steps = {"script": words > 20, "video": has(".mp4"), "srt": has(".srt"), "thumbnail": has("-thumbnail.png"),
                 "sheet": has("-youtube.txt"), "uploaded": bool(upinfo)}
    ready = all(steps[k] for k in ("video", "srt", "thumbnail", "sheet"))
    return {"name": n, "kind": kind, "title": sheet_title(p), "words": words, "steps": steps, "upload": upinfo, "yt": ytstate.badge_for(p),
            "ready": ready,
            "modified": max((f.stat().st_mtime for f in p.iterdir()), default=0)}

@app.get("/api/projects")
def projects():
    d, hide = Path(cfg()["projects_dir"]), set(cfg().get("hide_projects", []))
    out = [summary(p) for p in d.iterdir() if p.is_dir() and p.name not in hide and (p / "script.json").exists()] if d.exists() else []
    return jsonify(sorted(out, key=lambda s: -s["modified"]))

@app.get("/api/projects/<name>")
def project(name):
    p = proj_dir(name)
    s = summary(p)
    sheet = p / f"{name}-youtube.txt"
    s["sheet_text"] = sheet.read_text(encoding="utf-8") if sheet.exists() else ""
    script = store.read(p / "script.json", [])
    s["script"] = script if isinstance(script, list) else []
    if s["kind"] == "long":     # the research documents, shown read-only on the project page
        s["docs"] = {k: (p / f"{name}-{k}.{ext}").read_text(encoding="utf-8") for k, ext in (("sources", "md"), ("chapters", "txt"))
                     if (p / f"{name}-{k}.{ext}").exists()}
    return jsonify(s)

@app.put("/api/projects/<name>/sheet")
def save_sheet(name):
    text = body().get("text")
    if not isinstance(text, str): abort(400, "text must be a string")
    (proj_dir(name) / f"{name}-youtube.txt").write_text(text, encoding="utf-8")
    return jsonify(ok=True)

@app.put("/api/projects/<name>/script")
def save_script(name):
    sentences = body().get("sentences")
    if not isinstance(sentences, list): abort(400, "sentences must be a list")
    store.write(proj_dir(name) / "script.json", [str(s).strip() for s in sentences if str(s).strip()], indent=2)
    return jsonify(ok=True)

@app.delete("/api/projects/<name>")
def delete_project(name):
    """removes the project folder from disk (video, thumbnail, sources). The YouTube copy, if any, is untouched."""
    p = proj_dir(name)
    if p.resolve().parent != Path(cfg()["projects_dir"]).resolve(): abort(400, "not a project folder")
    if any(j["label"].endswith(" · " + name) and not j["done"] for j in JOBS.values()): abort(409, "a job is still running on this project")
    size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
    def unlock(fn, path, _):   # read-only files on Windows
        os.chmod(path, stat.S_IWRITE); fn(path)
    try:
        shutil.rmtree(p, onerror=unlock)
    except OSError as e:
        abort(500, f"could not delete everything ({e}). Close anything using that folder and try again.")
    (ROOT / "data" / "make" / f"{name}.json").unlink(missing_ok=True)
    return jsonify(ok=True, freed_mb=round(size / 1e6, 1))

@app.get("/media/<name>/<path:fname>")
def media(name, fname):
    p = proj_dir(name)
    if not re.match(r"^[\w.-]+\.(mp4|png|jpg|srt)$", fname): abort(400)
    return send_from_directory(p, fname)

ACTIONS = {   # what the buttons run: engine steps and uploader commands
    "voice": ("engine", ["voice"]), "check": ("engine", ["check"]), "video": ("engine", ["video"]),
    "thumb": ("engine", ["thumb"]), "sheet": ("engine", ["sheet"]), "new": ("engine", ["new"]), "chapters": ("engine", ["chapters"]),
    "upload-dry": ("uploader", ["upload", "--dry-run"]), "upload": ("uploader", ["upload"]), "comment": ("uploader", ["comment"]),
}

@app.post("/api/run")
def run():
    c, b = cfg(), body()
    act, name = b.get("action"), b.get("project", "")
    if act == "auth":
        return jsonify(start_job("YouTube sign-in", [c["python"], c["uploader"], "auth"], str(ROOT), unique=True))
    if act == "voice":
        # Never let the renderer silently fall back to its default (often English) TTS voice.
        p = proj_dir(name)
        audio = p / "audio" / "hindi-voice.wav"
        if not audio.is_file():
            abort(400, f"Record/import Hindi narration to {audio} first. Check Hindi alignment support before using the Voice action.")
        cmd = [c["python"], c["engine"], "voice", name, "--file", str(audio)]
        return jsonify(start_job(f"voice · {name}", cmd, str(ROOT), unique=True))
    if act == "spinoffs":      # identify self-contained Hindi Short adaptations from a finished long video
        p = proj_dir(name)
        if not (p / f"{name}.srt").exists(): abort(400, "this video has no .srt yet: build the video first")
        prompt = (f"Use the repo-local .claude/skills/shorts/SKILL.md and .claude/skills/hindi-script/SKILL.md on the finished long video {name}. The transcript is {p / (name + '.srt')}; the "
                  f"chapters are {p / (name + '-chapters.txt')} and the script is {p / 'script.json'}. Find the 5 best spans of 20 to 55 seconds that survive without the video around them "
                  "(a complete opening thought, a turn, an ending line). For each of the top 5 write: the timecodes, a NEW first line (score five options with "
                  "~/.claude/skills/yt-script/hookscore.py and keep the best, showing the score), different on-screen text for the first two seconds, a loop point, and the title. "
                  "Do not crop the 16:9 animation into a vertical frame. Identify the visual elements and scenes that must be redesigned in 9:16 using the documentary visual system. "
                  f"Write it all to {p / (name + '-shorts.md')} and finish by printing the ranked list. Do not make any video and do not touch other projects.")
        return jsonify(start_agent(f"spinoffs · {name}", prompt, c.get("options_model") or None, "feed"))
    if act not in ACTIONS or not SLUG.match(name or ""): abort(400, "bad action or project")
    tool, args = ACTIONS[act]
    cmd = [c["python"], c[tool], args[0], name] + args[1:]
    if tool == "uploader" and act != "comment":
        if b.get("now"): cmd.append("--now")                                   # publish immediately, public
        elif re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", b.get("at") or ""): cmd += ["--at", b["at"]]   # IST, from the time dropdown
        else: abort(400, "pick a date and a time first")
    if act == "video" and b.get("no_music"): cmd.append("--no-music")
    # unique: a double click returns the job that is already running instead of starting (and double-uploading) a second one
    return jsonify(start_job(f"{act} · {name}", cmd, str(ROOT), unique=True))

@app.post("/api/agent")
def agent():
    c = cfg()
    b = body()
    prompt = str(b.get("prompt", "")).strip()
    if not prompt: abort(400, "empty prompt")
    if b.get("duration") not in (None, "", 0):          # a chosen length is passed on to the skill as instructions
        try: seconds = int(float(b["duration"]))
        except (TypeError, ValueError): abort(400, "duration must be a number of seconds")
        if not 20 <= seconds <= 1800: abort(400, "duration must be between 20 seconds and 30 minutes")
        prompt += "\n\n" + topics.length_instructions(seconds)
    mode = "window" if (b.get("window") or c.get("agent_window")) else "feed"
    return jsonify(start_agent("agent · " + prompt[:50], prompt, mode=mode))


# ---------- schedule: YouTube is the truth, the planner only fills in what is still to come ----------
@app.get("/api/schedule")
def schedule():
    import ytstate
    refresh_youtube(force=bool(request.args.get("refresh")))
    vids = ytstate.STATE["videos"]
    prow, perr = planner.rows(cfg()["planner"])
    today, planned = dt.datetime.now(IST).date(), []
    for r in prow:
        if r["date"] < today - dt.timedelta(days=1) or r.get("status") in ("Posted", "Skipped"): continue
        if vids and ytstate.match_title(r.get("title"), vids, 0.78): continue    # already on YouTube: shown above with its real state
        planned.append({**r, "date": r["date"].isoformat(), "day": r["date"].strftime("%a")})
    return jsonify(youtube=vids, connected=ytstate.STATE["connected"], error=ytstate.STATE["error"], last=ytstate.STATE["last"],
                   planned=planned[:60], planner_error=perr)

@app.get("/api/next-slot")
def next_slot():
    """the first posting slot (not Long) that is in the future and has nothing live or scheduled around it"""
    import ytstate
    c, now = cfg(), dt.datetime.now(IST)
    taken = []
    for v in ytstate.STATE["videos"]:
        if v["state"] in ("scheduled", "live"):
            try: taken.append(dt.datetime.fromisoformat(v["when"]))
            except ValueError: pass
    slots = sorted(((n, t) for n, t in c["slots"].items() if n != "Long"), key=lambda x: x[1])
    for day in range(30):
        d = (now + dt.timedelta(days=day)).date()
        for name, hhmm in slots:
            h, m = map(int, hhmm.split(":"))
            t = dt.datetime(d.year, d.month, d.day, h, m, tzinfo=IST)
            if t < now + dt.timedelta(minutes=35) or any(abs((t - x).total_seconds()) < 3600 for x in taken): continue
            return jsonify(at=t.strftime("%Y-%m-%d %H:%M"), date=t.strftime("%Y-%m-%d"), time=hhmm, slot=name, checked_youtube=ytstate.STATE["connected"])
    return jsonify(at=None)

@app.post("/api/open-planner")
def open_planner():
    f = Path(cfg()["planner"])
    if not f.exists(): abort(404, f"no planner at {f}")
    os.startfile(f)
    return jsonify(ok=True)


import analytics, ytstate, topics   # noqa: E402
analytics.register(app, ROOT, cfg, start_job)
refresh_youtube = ytstate.register(app, ROOT, cfg)      # live posted / scheduled / private state for every tab
topics.register(app, ROOT, cfg, start_job, JOBS, start_agent)
import thumbs
thumbs.register(app, ROOT, cfg, start_agent, proj_dir, JOBS)   # five thumbnail ideas, then the picked one drawn   # topic selector + the "make this video" job


# ---------- settings and housekeeping ----------
def code_stamp():
    return max(f.stat().st_mtime for f in [*APP.glob("*.py"), *(APP / "static").glob("*")])
STARTED = code_stamp()

@app.get("/api/meta")
def meta():
    """shared lists (so the page never hard-codes them) and whether the code on disk is newer than this running copy"""
    cfg()
    return jsonify(types=topics.TYPES, voices=topics.VOICES, lengths=topics.LENGTHS, started=STARTED, current=code_stamp(), config_problem=_cfg["problem"],
                   restartable=bool(os.environ.get("BEAN_AUTORESTART")), busy=any(not j["done"] for j in JOBS.values()))

@app.post("/api/restart")
def restart():
    """start.bat runs the studio in a loop and starts it again on exit code 3: the page uses this to load newer code by itself"""
    if not os.environ.get("BEAN_AUTORESTART"): abort(400, "started without start.bat: close this console window and run start.bat again")
    threading.Timer(0.5, lambda: os._exit(3)).start()
    return jsonify(ok=True)

@app.get("/api/config")
def get_config():
    return jsonify(cfg())

@app.put("/api/config")
def put_config():
    new = request.get_json(silent=True)
    errs = validate_config(new)
    if errs: abort(400, "Not saved: " + "; ".join(errs))
    overrides = {k: v for k, v in new.items() if DEFAULTS.get(k, object()) != v}      # only what differs from the defaults
    if CONFIG.exists(): shutil.copy2(CONFIG, CONFIG.with_suffix(".json.bak"))
    CONFIG.write_text(json.dumps(overrides, indent=2), encoding="utf-8")
    return jsonify(ok=True, saved=len(overrides), note="Saved. Restart start.bat to apply a new port." if "port" in overrides else "Saved.")

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


def main():
    c = cfg()
    url = f"http://127.0.0.1:{c['port']}"
    import socket, urllib.request
    with socket.socket() as s:
        busy = s.connect_ex(("127.0.0.1", c["port"])) == 0
    if busy:                                   # already running: open it instead of crashing, and say if it is out of date
        try:
            running = json.loads(urllib.request.urlopen(url + "/api/meta", timeout=3).read())
            stale = running["started"] < code_stamp() - 1
        except Exception:
            stale = True
        print(f"Hindi Explainer Studio is already running at {url}.")
        if stale: print("That copy is OUT OF DATE (it started before the latest code). Close its console window, then run start.bat again.")
        if c.get("open_browser"): webbrowser.open(url)
        return
    print(f"Hindi Explainer Studio on {url}  (Ctrl+C to stop)")
    if _cfg["problem"]: print("WARNING:", _cfg["problem"])
    if c.get("open_browser"): threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=c["port"], debug=False, threaded=True)


if __name__ == "__main__":
    main()
