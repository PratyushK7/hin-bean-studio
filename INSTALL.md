# Installation

## 1. Local prerequisites

Windows is the supported baseline for the copied dashboard.

Install:
- Python 3.10 or later.
- Node.js (the animation renderer uses JavaScript and Playwright).
- FFmpeg and ffprobe on PATH.
- Claude Code CLI on PATH.
- The animation-skills kit used by the upstream Bean Studio renderer.

The upstream `bean-studio` repository did not vendor the complete animation renderer or the installed skill kit. See [engine/README.md](engine/README.md) before attempting to render.

## 2. Start the dashboard

Double-click `start.bat`. It creates `.venv`, installs `requirements.txt` and starts the Flask app at:

`http://127.0.0.1:5173`

Or run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe tools\build_planner.py
.venv\Scripts\python.exe app\server.py
```

Open the Settings tab. Paths are local settings; update `projects_dir`, `planner`, `python`, `engine`, `uploader` and `agent_cwd` if the defaults do not match your machine.

The default projects directory is `projects/`. The default planner is `data/planner.xlsx`.

## 3. Renderer and skills

The dashboard starts Claude Code jobs with the repository as its working directory. Claude Code should discover the repo-local skills under `.claude/skills/`.

Before making a video:
1. Confirm the configured renderer path exists.
2. Read `.claude/skills/hindi-explainer/SKILL.md`.
3. Verify the installed renderer's actual drawing API and current example project.
4. Confirm the renderer has a working Devanagari font and glyph shaping.
5. Confirm the human Hindi voice recording and speech aligner support Hindi. TTS is not enabled in the wizard yet.

Do not assume the original English-oriented Kokoro/Parakeet setup automatically works for Hindi. Run the short Hindi voice and subtitle smoke test described in [engine/README.md](engine/README.md).

## 4. YouTube connection

Follow [tools/yt_upload.md](tools/yt_upload.md). Put OAuth client and token files under `tools/.secrets/`. They are ignored by Git.

Enable both YouTube Data API v3 and YouTube Analytics API. Sign in from Activity or run:

```powershell
.venv\Scripts\python.exe tools\yt_upload.py auth
```

## 5. First production smoke test

Do not start with a 15-minute video.

1. Choose a low-risk topic with a small number of verifiable claims.
2. Complete `research.md`, `sources.md` and the claim ledger.
3. Approve a 30–45 second Hindi script and storyboard.
4. Record a short Hindi voice sample.
5. Verify voice duration, alignment, Devanagari subtitles and caption layout.
6. Render a 10–15 second scene test and inspect it.
7. Only then build the full Short.

## 6. Troubleshooting

- **Studio is open but the code is stale:** close the running console and start again.
- **Planner missing:** run `python tools/build_planner.py`.
- **Claude Code not found:** ensure `claude` is on PATH and configured in Settings.
- **Renderer missing:** fix the `engine` path in Settings; see [engine/README.md](engine/README.md).
- **Hindi captions render as boxes or broken characters:** install/configure a Devanagari-capable font in the renderer and verify glyph shaping. Do not proceed with the full video until the test passes.
- **Hindi word timings are wrong:** use a Hindi-capable aligner or sentence-level alignment. Do not trust the English aligner by default.
