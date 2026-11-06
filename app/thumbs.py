"""Hindi Explainer Studio: documentary thumbnail ideas and rendering for a finished video.
  1. POST /api/thumbnail/ideas {project}   an agent reads the video's script, title and current thumbnail and writes THREE different
                                           thumbnail ideas, each built on a different click trigger; GET /api/thumbnail/ideas/<project> reads them.
  2. POST /api/thumbnail/make {project, idea}   the picked idea is drawn (web/thumb.js), rendered, checked at feed size, fixed, and saved
                                           (the old one is kept as <project>-thumbnail-prev.png). Nothing is uploaded."""
import json, re, time
from pathlib import Path
from flask import abort, jsonify, request

TRIGGERS = ("Curiosity", "Scale", "Stakes", "Mystery", "Before / after", "Comparison", "Revelation")
ENGINE_SKILL = ".claude/skills/thumbnail"


def clean(v, n=300):
    return re.sub(r"\s+", " ", str(v or "")).strip()[:n]


def title_of(p):
    """the title from <project>-youtube.txt (the line under == TITLE ==), else ''"""
    f = p / f"{p.name}-youtube.txt"
    if f.exists():
        m = re.search(r"== TITLE ==\s*\n(.+)", f.read_text(encoding="utf-8", errors="replace"))
        if m: return m.group(1).strip()
    return ""


def words_of(v):
    """up to 3 words, upper case"""
    return " ".join(re.findall(r"[A-Za-z0-9$%'?!+\u2192-]+", str(v or "").upper())[:3])


def register(app, ROOT, cfg, start_agent, proj_dir, JOBS):
    def model(wide):
        if not wide: return cfg().get("thumbnail_model_short") or None      # a Short's thumbnail: the session default, ideas and drawing
        return cfg().get("thumbnail_model") or None

    def ideas_file(p): return p / f"{p.name}-thumb-ideas.json"          # the saved three (what the button shows)
    def new_file(p): return p / f"{p.name}-thumb-ideas-new.json"        # a reroll in progress: replaces the saved five only when it is done

    def label_of(name): return f"thumb ideas · {name}"

    def running_job(name):
        return next((j for j in JOBS.values() if j["label"] == label_of(name) and not j.get("done")), None)

    def load(path):
        try: return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        except Exception: return None

    def sanitise(raw):
        ideas = []
        for o in (raw if isinstance(raw, list) else []):
            if not isinstance(o, dict) or not clean(o.get("concept")): continue
            ideas.append({"name": clean(o.get("name"), 60) or "Idea", "trigger": o.get("trigger") if o.get("trigger") in TRIGGERS else "Curiosity",
                          "words": words_of(o.get("words")), "concept": clean(o.get("concept")), "subject": clean(o.get("subject"), 120),
                          "face": clean(o.get("face"), 120), "why": clean(o.get("why")), "risk": clean(o.get("risk"))})
        return ideas[:3]

    def harvest(p, jobs):
        """a finished batch that nobody collected (the window was closed): the agent's side file, else what it printed, else nothing"""
        ideas = sanitise(load(new_file(p)))
        for j in jobs:
            if ideas: break
            m = re.search(r"\[\s*\{.*\}\s*\]", "\n".join(j["log"]), re.S)
            try: ideas = sanitise(json.loads(m.group(0)) if m else None)
            except Exception: ideas = []
        if ideas:
            ideas_file(p).write_text(json.dumps(ideas, indent=1), encoding="utf-8"); new_file(p).unlink(missing_ok=True)
        return ideas

    @app.post("/api/thumbnail/ideas")
    def thumb_ideas():
        name = (request.get_json(silent=True) or {}).get("project", "")
        p = proj_dir(name)
        wide = (p / "project.json").exists() and "wide" in (p / "project.json").read_text(encoding="utf-8", errors="replace")
        if not (p / "script.json").exists(): abort(400, "this video has no script yet")
        busy = running_job(name)
        if busy: return jsonify(job=busy["id"], project=name, running=True)      # already analysing: reattach, don't pay for a second run
        out = new_file(p)
        out.unlink(missing_ok=True)                                              # never read a stale batch
        size = "1280x720 (16:9, web/thumb.js, one still shot)" if wide else "1080x1920 (9:16 cover, web/thumb.js, gridSafe)"
        THUMB_SKILL = ".claude/skills/thumbnail/SKILL.md" if wide else ".claude/skills/thumbnail/SKILL.md"
        prompt = f"""
You are the thumbnail strategist for the YouTube channel "{cfg()['channel']}": serious Hindi documentary explainers using editorial composition, data graphics and custom animation. The video is {name} in {p}.

Read: {p / 'script.json'} (the whole voiceover), {p / (name + '-youtube.txt')} (title and current thumbnail brief; title now: "{title_of(p) or 'unknown'}"), {p / (name + '-sources.md')} if it exists, {p / 'web' / 'cast.js'} (the visual system and evidence objects we can draw), and {p / (name + '-thumbnail.png')} if it exists (the current thumbnail).

Read {THUMB_SKILL} first and follow its rules for the words, the picture and the tests. The picture is {size}.

Then write THREE different thumbnail ideas, each built on a different click trigger from: {', '.join(TRIGGERS)}. At least one communicates a genuine consequence or stake the video supports, and at least one uses curiosity. Avoid fear-bait and shock-bait. Be unbiased and strict: rank them, best first.

Write a JSON array of exactly 3 objects to {out} and nothing else on disk (no other file changes). Each object:
{{"name": "3 to 6 word label", "trigger": one of the triggers, "words": "the on-image words, as the skill says", "concept": "the whole picture in two sentences: what is drawn, where, doing what", "subject": "the one dominant visual subject", "face": "which human subject or visual focal point, and what emotion", "why": "one sentence: what makes a stranger click and why the video pays it off", "risk": "one sentence: how this could mislead or fail, and how it is avoided"}}
Then print the array.
"""
        j = start_agent(label_of(name), prompt, model(wide), "plain")
        return jsonify(job=j["id"], project=name)

    @app.get("/api/thumbnail/ideas/<name>")
    def thumb_ideas_get(name):
        """What the button shows. Never starts a run. status: running | done | failed | none"""
        p = proj_dir(name)
        j = JOBS.get(request.args.get("job", "")) or running_job(name)
        if j and not j.get("done"):
            saved = sanitise(load(ideas_file(p)))
            return jsonify(status="running", ideas=[] if request.args.get("job") else saved, log=j["log"][-3:])
        finished = sorted((x for x in JOBS.values() if x["label"] == label_of(name) and x.get("done")), key=lambda x: x.get("started", 0), reverse=True)
        saved_at = ideas_file(p).stat().st_mtime if ideas_file(p).exists() else 0
        if request.args.get("job") or new_file(p).exists() or (finished and finished[0].get("started", 0) > saved_at):
            got = harvest(p, finished)                                           # a batch just finished (or finished unseen): it replaces the saved three
            if got: return jsonify(status="done", ideas=got)
            if request.args.get("job"): return jsonify(status="failed", ideas=sanitise(load(ideas_file(p))))
        saved = sanitise(load(ideas_file(p)))
        return jsonify(status="done" if saved else "none", ideas=saved)

    @app.post("/api/thumbnail/make")
    def thumb_make():
        b = request.get_json(silent=True) or {}
        p = proj_dir(b.get("project", "")); name = p.name
        i = b.get("idea") or {}
        concept = clean(i.get("concept"))
        if not concept: abort(400, "no idea picked")
        title = title_of(p)
        words = words_of(i.get("words"))
        wide = (p / "project.json").exists() and "wide" in (p / "project.json").read_text(encoding="utf-8", errors="replace")
        size = "1280x720 (16:9, web/thumb.js, one still shot)" if wide else "1080x1920 (9:16 cover, web/thumb.js, gridSafe)"
        THUMB_SKILL = ".claude/skills/thumbnail/SKILL.md" if wide else ".claude/skills/thumbnail/SKILL.md"
        py, eng = cfg()["python"], cfg()["engine"]
        prompt = f"""
You are drawing a better thumbnail for the video {name} in {p}. The user picked this idea from the three:
- name: {clean(i.get('name'), 60)}   trigger: {clean(i.get('trigger'), 30)}
- words on the picture: {clean(i.get('words'), 60) or '(as the skill says)'}
- concept: {clean(i.get('concept'))}
- the one big subject: {clean(i.get('subject'), 120)}   the focal subject: {clean(i.get('face'), 120)}
- why it clicks: {clean(i.get('why'))}   risk: {clean(i.get('risk'))}

Read {THUMB_SKILL} first and follow it. The picture is {size}. Then:
1. Read {p / 'script.json'}, {p / 'web' / 'cast.js'} and {p / (name + '-youtube.txt')}.
2. If {p / (name + '-thumbnail.png')} exists, copy it to {p / (name + '-thumbnail-prev.png')} first (keep the old one).
3. Write {p / 'web' / 'thumb.js'} for this idea only.
4. Run: {py} {eng} thumb {name}, then look at the small copy at feed size and the crops.
5. Judge the small copy with the skill's tests, and redraw until they all pass (at most 5 rounds).
6. Update the YouTube sheet's THUMBNAIL section (File:, Text:, Still:, Brief:) to match what you drew, and change nothing else in that file.
7. Finish by printing the final text, what is drawn, and the result of each test, honestly (say so if one still fails). Then upload nothing.
"""
        j = start_agent(f"thumb · {name}", prompt, model(wide), "feed")
        return jsonify(job=j["id"], project=name)
