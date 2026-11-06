"""Topic selector + video generator for Hindi Explainer Studio, for Shorts and long videos.

1. Finds what is working on other channels in the same category: public listings (yt-dlp, no login), each video scored as a
   multiple of its own channel's median views, so a big channel's normal day doesn't look like a hit. Shorts and long videos
   have separate pools and separate medians.
2. "Get 3 ideas": a sample of the best outliers goes to the agent, which adapts five of them into ORIGINAL topics for this
   channel (topic and format borrowed, never the script or title). "Re-roll" samples a fresh set, skipping sources already shown.
   data/picks.json holds hand-researched topics (with a brief file) that show above the generated ones.
3. A chosen topic + the answers from the form become one agent job. A Short is made with the hindi-explainer skill (9:16); a long video with
   the longform skill (16:9, chapters), both to a rendered video and upload sheet (a long video's thumbnail comes later, from the Better thumbnail button).

length_instructions(seconds) is the one place that turns a duration into instructions for the skill; the Agent tab uses it too.
register(app, ROOT, cfg, start_job, JOBS) adds /api/topics*.
"""
import concurrent.futures as cf, datetime as dt, difflib, json, random, re, statistics, subprocess, sys, threading, time, uuid
from pathlib import Path
from flask import abort, jsonify, request

import planner, store
from ytstate import norm

TYPES = ["Scenario", "Myth test", "Why", "True story", "Versus", "Ranking", "Timeline", "Paradox", "Puzzle",
         "How it works", "Superlative", "How many", "Map/scale", "Explainer"]
FMT = [("Scenario", r"^what if|^what would happen|^what happens"), ("How many", r"^how (many|much|long|far|big|fast|hot|cold|deep|high|old)"),
       ("Versus", r"\bvs\.?\b|versus"), ("Timeline", r"\blevels?\b"), ("Paradox", r"paradox"), ("Ranking", r"ranking|ranked|top \d+|\bworst\b|^\d+ "),
       ("Puzzle", r"which .* (first|more|faster)|puzzle|riddle|can you (guess|solve)"),
       ("Explainer", r"explained|the science of|everything you need|\ball the\b"),
       ("How it works", r"^how (do|does|did|is|are|was|to)\b|how .* works?"), ("Why", r"^why\b|\bwhy\b"),
       ("Superlative", r"\b(most|deadliest|largest|biggest|smallest|fastest|strongest|oldest|longest|rarest|sharpest)\b"),
       ("Map/scale", r"further|bigger than|smaller than|size of|\bmap\b"),
       ("True story", r"\b(1[0-9]{3}|20[0-2][0-9])\b|\bstory\b|history|disaster|incident|what happened"),
       ("Myth test", r"^(is|are|can|could|does|do)\b|myth|actually|really|truth")]
OFF_BRAND = re.compile(r"porn|adult content", re.I)  # do not filter serious politics, conflict or history
STOP = set("what if you your the a an of to how would it take and is are do does why can could in on for with from at".split())
VOICES = [["own_recording", "Own Hindi voice recording (recommended)"]]
VOICE_IDS = [v[0] for v in VOICES]
LENGTHS = {"short": [30, 40, 50, 60], "long": [480, 600, 720, 900]}       # seconds
WORDS_PER_SECOND = 2.4                                                       # rough script planning only; Hindi audio timing is authoritative
KINDS = ("short", "long")


def length_instructions(seconds):
    """Create a target-duration brief without assuming English TTS or alignment works for Hindi."""
    seconds = int(seconds)
    words = round(seconds * WORDS_PER_SECOND)
    head = (f"TARGET LENGTH: {seconds} seconds of Hindi narration. About {words} words is only a rough drafting estimate; "
            "the actual recording duration and verified Hindi alignment are authoritative. Use the voiceover skill.")
    if seconds <= 60:
        return (head + " This is a 9:16 Short. Create and listen to the Hindi voice track, verify the aligner supports Hindi, "
                "then storyboard and render only after the script and claims are checked.")
    return (head + " This is a 16:9 long-form video. Use the longform skill, 5 to 9 chapters, a research-backed narrative, "
            "and scene-by-scene code-generated documentary graphics. Do not stretch the runtime or fabricate word timings.")


def classify(title):
    for name, pat in FMT:
        if re.search(pat, title, re.I): return name
    return "Other"


def too_close(title, others, cutoff=0.72):
    t = norm(title)
    return any(difflib.SequenceMatcher(None, t, norm(o)).ratio() >= cutoff for o in others)


def clean(s, n=500):
    return re.sub(r"[\x00-\x1f\x7f]", " ", str(s or "")).strip()[:n]


def kind_of(v):
    return v if v in KINDS else "short"


def register(app, ROOT, cfg, start_job, JOBS, start_agent=None):
    DATA = ROOT / "data"

    def run_agent(label, prompt, model=None, mode="plain"):
        """the studio's start_agent (live feed / own window); a plain job when none is given (tests)"""
        if start_agent: return start_agent(label, prompt, model, mode)
        cmd = list(cfg()["agent_command"]) + (["--model", model] if model else [])
        return start_job(label, cmd + [prompt], cfg()["agent_cwd"])

    POOL = {"short": DATA / "topic-pool.json", "long": DATA / "topic-pool-long.json"}
    STATEF, PICKS = DATA / "topic-state.json", DATA / "picks.json"
    st = {k: {"refreshing": False, "progress": "", "error": None} for k in KINDS}
    st["batches"] = {}
    lock = threading.Lock()

    load_json, save_json = store.read, store.write

    # ---------- 1. the pool of outliers ----------
    def fetch_channel(handle, kind):
        short = kind == "short"
        url = f"https://www.youtube.com/@{handle.lstrip('@')}/{'shorts' if short else 'videos'}"
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--playlist-end", "50" if short else "45", "--no-warnings", url],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=150)
        d = json.loads(r.stdout)
        ents = [e for e in (d.get("entries") or []) if e and e.get("view_count")]
        if not short:                                 # long-form means an actual episode: 4 to 40 minutes, not a Short or a live stream
            ents = [e for e in ents if 240 <= (e.get("duration") or 0) <= 2400]
        if len(ents) < (8 if short else 6): return []
        med = statistics.median(e["view_count"] for e in ents)
        name = d.get("channel") or d.get("uploader") or handle
        out = []
        for e in ents:
            t = re.sub(r"\s*#\S+", "", e.get("title", "")).strip()
            out.append({"id": e["id"], "title": t, "channel": name, "views": e["view_count"], "multiple": round(e["view_count"] / med, 2),
                        "type": classify(t), "duration": e.get("duration"),
                        "url": f"https://www.youtube.com/{'shorts/' if short else 'watch?v='}{e['id']}"})
        return out

    def refresh_pool(kind):
        with lock:
            s = st[kind]
            s.update(refreshing=True, error=None, progress="starting")
            chans = cfg().get("topic_channels", [])
            vids, done, failed = [], 0, []
            try:
                with cf.ThreadPoolExecutor(6) as ex:
                    futs = {ex.submit(fetch_channel, h, kind): h for h in chans}
                    for f in cf.as_completed(futs):
                        done += 1; s["progress"] = f"{done}/{len(chans)} channels"
                        try: vids += f.result()
                        except Exception: failed.append(futs[f])
                if not vids: raise RuntimeError("no videos came back; check your internet connection or the channel handles in Settings")
                save_json(POOL[kind], {"fetched": dt.datetime.now().isoformat(timespec="seconds"), "videos": vids, "failed": failed})
            except Exception as e:
                s["error"] = str(e)[:300]
            finally:
                s.update(refreshing=False, progress="")

    # ---------- 2. five ideas, and re-roll ----------
    def already_made():
        c = cfg(); names = []
        for sheet in Path(c["projects_dir"]).glob("*/*-youtube.txt"):
            m = re.search(r"== TITLE ==\s*\n(.+)", sheet.read_text(encoding="utf-8"))
            if m: names.append(m.group(1).strip())
        names += [p.name.replace("-", " ") for p in Path(c["projects_dir"]).iterdir() if p.is_dir()]
        names += planner.titles(c["planner"])
        try:
            import ytstate
            names += [v["title"] for v in ytstate.STATE["videos"]]
        except Exception: pass
        return names

    def pick_candidates(pool, seen, made, k=14):
        def ok(v, floor):
            return v["multiple"] >= floor and not OFF_BRAND.search(v["title"]) and not too_close(v["title"], made)
        for floor in (1.5, 1.2, 1.0):            # relax if the pool is small (few channels)
            cands = [v for v in pool if ok(v, floor) and v["id"] not in seen]
            if len(cands) < 8:                   # shown everything good at this level: start over
                cands = [v for v in pool if ok(v, floor)]
                seen.clear()
            if len(cands) >= 5: break
        cands.sort(key=lambda v: -v["multiple"] * random.uniform(0.6, 1.4))
        chosen, per_type = [], {}
        for v in cands[:80]:
            cap = 6 if v["type"] == "Other" else 3
            if per_type.get(v["type"], 0) >= cap: continue
            per_type[v["type"]] = per_type.get(v["type"], 0) + 1; chosen.append(v)
            if len(chosen) >= k: break
        if len(chosen) < 10:                     # too few types in the pool for the per-type cap: top up without it
            chosen += [v for v in cands if v not in chosen][:10 - len(chosen)]
        return chosen

    def strings(v, n, size):
        return [clean(x, size) for x in v[:n] if isinstance(x, str)] if isinstance(v, list) else []

    def finish_batch(b):
        """read the agent's answer; fall back to the raw best outliers if it didn't produce one"""
        opts = None
        try:
            opts = json.loads(Path(b["out"]).read_text(encoding="utf-8")) if Path(b["out"]).exists() else None
        except Exception: opts = None
        if not opts:
            j = JOBS.get(b["job"]); text = "\n".join(j["log"]) if j else ""
            m = re.search(r"\[\s*\{.*\}\s*\]", text, re.S)
            try: opts = json.loads(m.group(0)) if m else None
            except Exception: opts = None
        good = []
        for o in (opts or []):
            if isinstance(o, dict) and o.get("title") and isinstance(o.get("inspired_by"), dict):
                o["type"] = o.get("type") if o.get("type") in TYPES else "Other"
                for k in ("promise", "visual", "fact_note"): o[k] = clean(o.get(k), 300)
                o["fact_risk"] = o.get("fact_risk") if o.get("fact_risk") in ("low", "medium", "high") else "medium"
                if b["kind"] == "long":
                    o["chapters"] = strings(o.get("chapters"), 9, 80); o["reuse_shorts"] = strings(o.get("reuse_shorts"), 6, 80)
                    o["sources_to_check"] = strings(o.get("sources_to_check"), 6, 120)
                    try: o["runtime_min"] = int(min(15, max(8, float(o.get("runtime_min") or 10))))
                    except (TypeError, ValueError): o["runtime_min"] = 10
                o["adapted"] = True; good.append(o)
        if len(good) < 3:                         # fill up (or replace) with the raw outliers, clearly marked
            for c in b["candidates"]:
                if len(good) >= 3: break
                good.append({"title": c["title"], "type": c["type"], "promise": "", "visual": "", "fact_risk": "medium", "fact_note": "",
                             "inspired_by": {"title": c["title"], "channel": c["channel"], "multiple": c["multiple"], "url": c["url"]}, "adapted": False})
        for i, o in enumerate(good[:3]): o["n"] = i
        b["options"], b["status"] = good[:3], "ready"
        save_json(DATA / f"topic-last-{b['kind']}.json", {"options": good[:3], "when": dt.datetime.now().isoformat(timespec="seconds")})   # shown again on the next visit

    @app.get("/api/topics")
    def topics_get():
        kind = kind_of(request.args.get("kind"))
        pool = load_json(POOL[kind], None)
        s = st[kind]
        return jsonify(kind=kind, refreshing=s["refreshing"], progress=s["progress"], error=s["error"],
                       fetched=pool and pool["fetched"], videos=pool and len(pool["videos"]), failed=pool and pool.get("failed", []),
                       channels=cfg().get("topic_channels", []), category=cfg().get("topic_category", ""),
                       top=(pool and sorted(pool["videos"], key=lambda v: -v["multiple"])[:8]) or [])

    @app.get("/api/topics/picks")
    def topics_picks():
        """hand-researched topics (data/picks.json), shown above the generated ideas"""
        kind = kind_of(request.args.get("kind"))
        picks = (load_json(PICKS, {}) or {}).get(kind, [])
        last = load_json(DATA / f"topic-last-{kind}.json", {}) or {}
        return jsonify(picks=[dict(p, n=i, pick=True, adapted=True) for i, p in enumerate(picks)], last=last.get("options", []), last_when=last.get("when"))

    @app.post("/api/topics/refresh")
    def topics_refresh():
        kind = kind_of((request.get_json(silent=True) or {}).get("kind"))
        if not any(s["refreshing"] for k, s in st.items() if k in KINDS):
            threading.Thread(target=refresh_pool, args=(kind,), daemon=True).start()
        return jsonify(ok=True)

    @app.post("/api/topics/options")
    def topics_options():
        kind = kind_of((request.get_json(silent=True) or {}).get("kind"))
        pool = load_json(POOL[kind], None)
        if not pool: abort(400, "no source data yet: press 'Refresh sources' first")
        state = load_json(STATEF, {"seen": []})
        skey = "seen" if kind == "short" else "seen_long"
        seen = set(state.get(skey, [])); made = already_made()
        cands = pick_candidates(pool["videos"], seen, made)
        if len(cands) < 3: abort(400, f"only {len(cands)} usable source videos out of {len(pool['videos'])} (after removing topics you already made); refresh sources or add more channels in Settings")
        bid = uuid.uuid4().hex[:8]
        out = DATA / f"topic-options-{bid}.json"
        cfile = DATA / f"topic-candidates-{bid}.json"
        save_json(cfile, {"candidates": cands, "already_made_titles": made[:150], "types": TYPES})
        c = cfg()
        if kind == "short":
            what = ("serious Hindi-language documentary Shorts, 30 to 60 seconds, with one clear question, verified explanation and a strong visual idea; use natural spoken Hindi, retaining standard English technical terms when clearer",
                    "recent Shorts and short-form explainers", "answerable in concise Hindi narration with a traceable factual payoff",
                    '{"title": str, "type": one of the types, "promise": "one sentence on what the video shows and the answer it lands on", "visual": "one line: what we would draw", "fact_risk": "low"|"medium"|"high", "fact_note": "what must be checked", "inspired_by": {"title": source title, "channel": source channel, "multiple": number, "url": source url}}')
        else:
            what = ("serious Hindi-language documentary explainers, with a clear thesis, sourced evidence, causal reasoning and a defensible conclusion; no mascots, comedy requirement or forced hypothetical framing. This is for a LONG video of 8 to 15 minutes (landscape), built around a central question with 5 to 9 chapters",
                    "recent long-form videos (4 to 40 minutes)", "able to sustain 8 to 15 minutes with primary sources, expert references, official data and a coherent chapter structure",
                    '{"title": str, "type": one of the types, "promise": "one sentence: the premise and the answer it lands on", "visual": "one line: the central visual metaphor, graphic or documentary evidence that explains the idea", "chapters": [5 to 9 short chapter titles in order], "runtime_min": 8 to 15, "reuse_shorts": [titles of OUR made or planned Shorts it could fold in or spin off, if any], "sources_to_check": [3 to 5 named studies, reviews or agencies that would back it], "fact_risk": "low"|"medium"|"high", "fact_note": "what must be checked", "inspired_by": {"title": source title, "channel": source channel, "multiple": number, "url": source url}}')
        prompt = f"""You are the topic scout for the YouTube channel "{c['channel']}": {what[0]}. Category: {c.get('topic_category', 'science explainers')}.

Read {cfile}. "candidates" are {what[1]} from other channels that beat their own channel's median views by the "multiple" shown. "already_made_titles" are topics we have made or planned: never repeat or closely echo them.

Pick THREE different candidates and adapt each into an ORIGINAL topic for our channel. Borrow the topic area and the video format only: never copy a title, a script or a distinctive phrase. Rules:
- 3 different video types (from {TYPES}); at most one speculative scenario, and only when counterfactual reasoning is central to the subject. Write the title and idea promise in natural Hindi (Devanagari); retain a familiar English technical term when clearer. Title in the channel voice: a plain question or claim, under 60 characters, no hype words, no all caps.
- Every topic must be explainable through an intentional visual system (maps, data, timelines, diagrams, code-generated animation, real visual references), without relying on mascots or decorative motion, and {what[2]}.
- Vary the subject areas across the three. Prefer topics with high public relevance, strong evidence and a visual model that improves understanding.
- Do not force sensational, conspiratorial or outrage-driven framing onto any topic.
- Only topics whose facts you are confident about, or flag the risk honestly.
- Prefer the highest "multiple", but variety beats ranking.

Write a JSON array of exactly 3 objects to {out} and nothing else on disk. Each object:
{what[3]}
Do not browse beyond the topic candidates for idea generation; mark every claim that will need primary-source verification during the research step. When done, also print the same JSON array as your final message."""
        j = run_agent(f"topics · 3 {kind} ideas", prompt, c.get("options_model") or None, "plain")
        b = {"id": bid, "kind": kind, "job": j["id"], "out": str(out), "status": "running", "candidates": cands, "options": [], "started": time.time()}
        st["batches"][bid] = b
        state[skey] = list(seen | {x["id"] for x in cands})[-400:]
        save_json(STATEF, state)
        return jsonify(batch=bid, job=j["id"])

    @app.get("/api/topics/batch/<bid>")
    def topics_batch(bid):
        b = st["batches"].get(bid) or abort(404, "unknown batch (server restarted?)")
        j = JOBS.get(b["job"])
        if b["status"] == "running" and j and j["done"]: finish_batch(b)
        return jsonify(status=b["status"], options=b["options"], seconds=int(time.time() - b["started"]),
                       log=(j["log"][-4:] if j and b["status"] == "running" else []))

    # ---------- 3. the form's answers -> the finished video (Short 9:16, long 16:9) ----------
    def slug_for(title):
        words = [w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOP][:4] or ["hindi-topic-" + uuid.uuid4().hex[:6]]
        base = "-".join(words)[:40].strip("-") or "video"
        d, slug, n = Path(cfg()["projects_dir"]), base, 2
        while (d / slug).exists(): slug, n = f"{base}-{n}", n + 1
        return slug

    def number(v, default, lo, hi):
        try: return min(hi, max(lo, float(v)))
        except (TypeError, ValueError): return default

    @app.post("/api/topics/make")
    def topics_make():
        b = request.get_json(silent=True) or {}
        t, a, c = b.get("topic") or {}, b.get("answers") or {}, cfg()
        kind = kind_of(b.get("kind"))
        title = clean(t.get("title"), 120)
        if not title: abort(400, "no topic")
        voice = a.get("voice") if a.get("voice") in VOICE_IDS else "own_recording"
        speed = round(number(a.get("speed"), 1.0, 0.9, 1.15), 2)
        dur = int(number(a.get("minutes"), 10, 8, 15) * 60) if kind == "long" else int(number(a.get("duration"), 40, 25, 60))
        slug = slug_for(title)
        (Path(c["projects_dir"]) / slug).mkdir(parents=True, exist_ok=True)     # reserve the name: a second click can't pick it too
        src = t.get("inspired_by") or {}
        brief = ""
        if t.get("brief"):                                                       # a researched pick: the agent must follow its brief
            bp = (ROOT / str(t["brief"])).resolve()
            if ROOT.resolve() in bp.parents and bp.is_file(): brief = str(bp)
        if kind == 'short':
            thumb_line = 'make it at make time: follow .claude/skills/thumbnail/SKILL.md'
        elif a.get('thumb_now'):
            thumb_line = 'the user chose to draw it now: follow .claude/skills/thumbnail/SKILL.md after the video'
        else:
            thumb_line = 'do NOT make one at make time: a long video gets its own from the Better thumbnail button (three ideas, the user picks one)'
        old6_text = f'6. NO thumbnail: do not write web/thumb.js, do not run build.py thumb, do not create a thumbnail file. Write {slug}-youtube.txt for a long video (the Hindi Explainer Studio YouTube packaging rules, but its THUMBNAIL section is the single line "Not made yet: use the Better thumbnail button in Hindi Explainer Studio", and check the title length and accuracy without --thumb: no #shorts, chapters from {slug}-chapters.txt, 6 to 8 sources, tags, a pinned comment, no list of spin-off Shorts: the user has a separate button for that).'
        step6 = (f"6. Thumbnail: draw it now, following .claude/skills/thumbnail/SKILL.md (longform step 10): web/thumb.js, build.py thumb {slug}, check stills/thumb-crops.png, and the YouTube sheet's THUMBNAIL section with the real File, Text, Still and Brief. Then {slug}-youtube.txt (the Hindi Explainer Studio packaging rules, no #shorts, chapters from {slug}-chapters.txt, 6 to 8 sources, tags, and check the title length and accuracy --thumb \"<the thumbnail words>\")."
                 if a.get('thumb_now') and kind == 'long' else old6_text)
        common = f"""TOPIC: {title}
Video type: {clean(t.get('type'), 40)}
What it shows: {clean(t.get('promise'), 300)}
What we would draw: {clean(t.get('visual'), 200)}
Fact to check carefully: {clean(t.get('fact_note'), 200)}
Inspired by (topic and format only; do not reuse its script or title): "{clean(src.get('title'), 120)}" from {clean(src.get('channel'), 60)}
{('RESEARCH BRIEF (read it first and follow it; its notes on what to verify and what NOT to claim override your own assumptions): ' + brief) if brief else ''}
PROJECT NAME: {slug}\nPYTHON: {c['python']}\nENGINE SCRIPT: {c['engine']}\nPROJECTS DIRECTORY: {c['projects_dir']}\nCreate it with the configured engine: "{c['python']}" "{c['engine']}" new {slug} (add --wide for long-form).

THE USER'S ANSWERS (follow them):
- {length_instructions(dur)}
- Voice: {voice}. For own_recording, the required file is {slug}/audio/hindi-voice.wav. Use no TTS fallback. Verify Hindi alignment support; never assume English voice timing applies to Hindi.\n- Voice gate: if own_recording is selected and the Hindi WAV is missing, stop after the research, Hindi script and storyboard. Do not invoke the renderer's default TTS, do not fabricate word timings, and do not render the full video. Report the exact audio path needed.
- Tone: {clean(a.get('tone') or 'serious, clear, composed and engaging', 80)}
- Visual treatment: use the documentary visual system; no recurring mascot characters. Use visual metaphors only when they clarify a mechanism.
- Ending: {clean(a.get('ending') or 'a concise evidence-based conclusion that resolves the opening question', 80)}
- Background music: {'on, and it follows the script: musicMood() follows the narrative tone and evidence (if supported by the renderer)' if a.get('music', True) else 'off (pass --no-music to build.py video)'}
- Channel outro: {'appended' if a.get('outro', True) else 'left off (pass --no-outro to build.py video)'}
- Thumbnail: {thumb_line}.
- Extra notes: {clean(a.get('notes'), 400) or 'none'}
"""
        if kind == "short":
            prompt = f"""Make a new Short with the hindi-explainer skill. Read .claude/skills/hindi-explainer/SKILL.md and the files it points to (.claude/skills/hindi-explainer/references/visual-language.md and .claude/skills/hindi-explainer/references/editorial-standards.md) first, and .claude/skills/hindi-explainer/references/channel-voice.md for the channel voice.

{common}
The user has approved the topic and settings. Complete the research, Hindi script and storyboard, but stop before rendering if high-impact factual claims remain unresolved or the selected Hindi voice track is not ready. For own_recording, if audio/hindi-voice.wav is absent, do not use default TTS; stop and report the required recording path. Keep it lean (a typical Short is about 30 tool calls): read each reference file once and do not re-read it; write five hook candidates and select the clearest one using the hook criteria in .claude/skills/hindi-script/SKILL.md; at most 6 web searches or fetches in total; write each file with one Write, not many small edits; check the stills in at most two rounds; then research, script, fact-check (search authoritative sources; hedge uncertainty; write sources.md), storyboard, scene code, the configured renderer's check, stills of every shot checked for overlaps and Devanagari caption placement, final video render, contact sheet, the thumbnail (SKILL.md step 9) and the YouTube upload sheet (step 10). Do not upload anything and do not touch other projects. Finish by printing the project folder, the title and the thumbnail text."""
        else:
            structure = clean(a.get("structure") or "as in the research brief or the topic's chapters", 80)
            prompt = f"""Make a LONG video ({dur // 60} minutes, 16:9) for the channel with the longform skill. Read .claude/skills/longform/SKILL.md and .claude/skills/longform/references/wide-storytelling.md, then .claude/skills/hindi-explainer/SKILL.md and its references, and .claude/skills/hindi-explainer/references/channel-voice.md for the channel voice. Use .claude/skills/longform/SKILL.md and the repository editorial standards for chapters, description and title.

{common}- Structure: {structure}

The user has approved the topic and settings. Complete the research, Hindi script and storyboard, but stop before rendering if high-impact factual claims remain unresolved or the selected Hindi voice track is not ready. If own_recording is selected and audio/hindi-voice.wav is absent, do not use default TTS; stop and report the required recording path. Continue in this order only when the voice gate is satisfied:
1. "{c['python']}" "{c['engine']}" new {slug} --wide (it lands in {c['projects_dir']}). The HOOK first, with .claude/skills/hindi-script/SKILL.md: draft five candidate openings, evaluate promise, specificity and accuracy, and record the chosen hook plus rationale in {slug}-hooks.md; then the turn by 0:45, no channel intro and no subscribe pitch. script.json: one sentence per entry, written chapter by chapter, a payoff that calls back to the hook. Calm, precise, evidence-led Hindi narration, with a memorable visual explanation at each chapter turn; no hype words.
2. Fact-check every claim with web searches of primary sources (the paper, the review, the agency page). Hedge what is uncertain, drop what you cannot verify, never invent a number. Write {slug}-sources.md: claim, link, and how far you verified it (full text, abstract only, secondary report).
3. chapters.json (5 to 9 chapters with renderer-compatible sentence indices). Use the voiceover skill to create and verify the Hindi audio and its timings. Only run the configured renderer's voice/alignment command if the installed aligner has passed a Hindi smoke test; otherwise use the approved Hindi-capable aligner. Generate valid YouTube chapter timestamps from the real aligned audio.
4. The SCENE AND SOUND PLAN: {slug}-plan.md, one row per chapter with the explanatory job, the visual form, scene composition, evidence IDs and sound rationale (see .claude/skills/longform/references/wide-storytelling.md). Then create web/cast.js for shared visual primitives and web/shots/ch01.js, ch02.js, ... ONE CHAPTER AT A TIME: write the chapter's scene code, render 2 or 3 representative stills per chapter, inspect the contact sheet, fix errors, then continue. Invoke every renderer command through the configured interpreter and engine script recorded above. The renderer check must show no errors or missing visual references; avoid long static shots and use scene/sound controls only when they exist in the installed API.
   Burned-in captions: {'ON (set CAP.on = true at the top of cast.js)' if a.get('captions') else 'OFF, the long-form standard: the .srt is uploaded as YouTube captions; put numbers and key words on screen as label shapes'}.
5. Run the configured engine's video command for {slug} (add --no-music or --no-outro only when selected), then run its sheet command and inspect the contact sheet once.
6. {step6}
Do not upload anything and do not touch other projects. Finish by printing the project folder, the real length, the chapters, the title, and anything you could not verify (the thumbnail is made afterwards from the Better thumbnail button)."""
        (DATA / "make").mkdir(parents=True, exist_ok=True)
        save_json(DATA / "make" / f"{slug}.json", {"kind": kind, "topic": t, "answers": a, "when": dt.datetime.now().isoformat(timespec="seconds")})
        mode = "window" if (a.get("window") or c.get("agent_window")) else "feed"      # watch it live, or in its own Claude window
        model = a.get("model") if a.get("model") in ("opus", "sonnet", "haiku") else None
        j = run_agent(f"make · {slug}", prompt, model, mode)
        return jsonify(job=j["id"], project=slug, title=title, kind=kind, mode=mode)
