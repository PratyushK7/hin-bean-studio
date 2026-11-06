# Hindi Explainer Studio

A local-first production desk for a serious Hindi explainer channel. It combines the operational workflow of Bean Studio with a hybrid documentary visual language: code-generated animation, diagrams, maps, charts and timelines, with carefully selected visual references where they genuinely help explain the subject.

**This is a separate project from `beanwithbadideas`.** It reuses the production architecture, not the comedy brand or its channel data.

## What carries over from Bean Studio

- Flask localhost dashboard with Videos, Topics, Schedule, Analytics, Agent, Activity and Settings tabs.
- Project folders, build-job de-duplication, live logs and file-based progress.
- YouTube channel state, scheduling/upload workflow and Analytics API integration.
- Topic scouting from public channel uploads, outlier scoring against each source channel's own median, and original topic adaptation.
- Atomic local JSON storage, planner integration, bounded logs, duplicate-upload protection and localhost request guards.
- The existing configurable rendering-engine interface for 9:16 Shorts and 16:9 long-form videos.

## What is different

- Hindi-first scripts, titles, narration, descriptions and subtitles.
- Serious documentary voice: analytical, composed, accessible and evidence-led. No bean characters, jokes-for-the-sake-of-jokes, or forced "what if" framing.
- A hybrid visual system: programmatic vector animation and motion graphics as the default; maps, charts, timelines, labelled diagrams, and researched stills as supporting visual evidence.
- Primary-source research, claim-level verification, uncertainty labels and source notes are required before script approval.
- Long-form storytelling is built around a central question, causal explanation, evidence, counterpoints and a clear conclusion.

## Requirements

- Windows is currently the easiest supported path because `start.bat` uses Windows process and file APIs.
- Python 3.10+, Node.js, FFmpeg/ffprobe, Claude Code CLI and the animation-skills kit used by the line-boil renderer.
- A working local line-boil engine installation. The upstream Bean Studio repository did **not** contain the complete engine or animation kit; it referenced an installed copy under `~/.claude/skills/line-boil/engine`. This repository keeps that dependency configurable rather than pretending the missing engine source was copied.
- A Google Cloud OAuth desktop client and YouTube Data API v3 + YouTube Analytics API for channel integration.

## Quick start

1. Read [INSTALL.md](INSTALL.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
2. Run `start.bat` to create the virtual environment and install Python dependencies.
3. Run `python tools/build_planner.py` once to create a clean planner workbook.
4. Set the paths and posting slots in Settings. The default renderer path points to the existing Bean Studio line-boil engine; change it if you install the engine elsewhere.
5. Add OAuth files under `tools/.secrets/` and follow [tools/yt_upload.md](tools/yt_upload.md).
6. Start with `.claude/skills/hindi-explainer/SKILL.md`. For a new video, research first, approve the Hindi script and storyboard, then record your narration at `projects/<slug>/audio/hindi-voice.wav`. The Voice action will not silently use the renderer's default English TTS. Complete the Hindi alignment smoke test and set `hindi_alignment_ready=true` in Settings before invoking alignment or full rendering.

## Project layout

```
app/                    Flask app and browser UI, adapted from Bean Studio
.claude/skills/         Hindi documentary production skills
docs/                   Editorial, architecture and pipeline contracts
engine/                 Renderer integration contract and setup checks
projects/               Local video projects (generated media is git-ignored)
data/                   Local state (no channel credentials or private stats committed)
research/               Research notes and source manifests
templates/project/      Starter project files
tools/                  YouTube uploader, planner builder, tests and setup checks
```

## Safety and privacy

- The web server binds to `127.0.0.1` only and checks Host/Origin to reduce cross-site and DNS-rebinding risks.
- OAuth client secrets and tokens are kept in `tools/.secrets/` and must never be committed.
- Upload actions require a deliberate user action and a confirmation in the UI. The uploader prevents accidental duplicate uploads.
- Research outputs should preserve source URLs and access dates. Do not store passwords, private user data or scraped personal information in project files.
- The app is a personal local production tool, not a hosted multi-user service.

## Important limitations

- The renderer's word aligner must be tested with Hindi recordings before relying on automatic word-level timing. Use your own Hindi narration WAV and inspect the generated timings; do not assume an English-oriented alignment model handles Hindi correctly.
- YouTube Analytics is delayed and does not expose every Studio metric. The dashboard documents proxy metrics rather than presenting them as exact equivalents.
- Until the Google API project passes YouTube's required audit, API uploads may be restricted to Private. See the uploader setup guide.
- The visual engine remains an external local dependency in this initial scaffold. The skills define the Hindi documentary production contract; they do not claim to bundle the upstream animation kit.

## Credits and lineage

The dashboard, local job orchestration, planner, YouTube integration, analytics sync and project workflow are adapted from [PratyushK7/bean-studio](https://github.com/PratyushK7/bean-studio). This repository changes the editorial system and brand for a separate Hindi explainer channel.
