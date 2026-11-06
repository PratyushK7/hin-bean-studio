# UPI local Canvas renderer

This project contains 16 deterministic 1920×1080 explanatory motion-graphics scenes for the UPI video.

## Why this renderer is separate

The installed line-boil renderer is not vendored in this repository, and its local drawing API cannot be inspected from GitHub. The scene code here therefore uses a self-contained HTML Canvas renderer with a documented capture interface instead of inventing calls into the unavailable renderer.

The visual design follows the repo's hindi-explainer, longform, storyboard and visual-engine skills:
- premium documentary palette: navy, warm off-white, teal and restrained amber;
- Roman-script Hinglish labels;
- source-conscious illustrative diagrams; no bank logos, real account data or fake official app screens;
- code-drawn QR illustration, payment network, debit/credit ledgers, authorization, pending states and safety comparison;
- deterministic frame rendering with no external image or network dependency.

## Requirements on Windows

- Node.js 20.9 or later.
- FFmpeg and ffprobe available on PATH.
- Your existing local Hindi Explainer Studio Python environment.
- A real voice recording at ../audio/hindi-voice.wav for the final MP4. The full render does not substitute English TTS.

## Install the local renderer

Open PowerShell in this folder:

    cd projects/upi-behind-the-scan/render
    npm install
    npx playwright install chromium

Check dependencies:

    python build.py check upi-behind-the-scan

## Preview all 16 scenes (no voice recording needed)

    npm run preview -- --out ./stills

This writes one PNG per storyboard scene to render/stills/. Inspect layout, font rendering and scene logic before rendering the full video.

## Render the full video

First record your own narration and save it as:

    projects/upi-behind-the-scan/audio/hindi-voice.wav

Then run:

    npm run render -- --audio ../audio/hindi-voice.wav --out ../upi-behind-the-scan.mp4

Optional settings:

    npm run render -- --audio ../audio/hindi-voice.wav --out ../upi-behind-the-scan.mp4 --fps 24 --quality 92

The default is 24 fps, 1920×1080, H.264 video with AAC narration. Frames are captured from the local browser and streamed to FFmpeg; the renderer does not create thousands of intermediate image files.

## Existing local dashboard integration

You can run the adapter directly:

    python build.py check upi-behind-the-scan
    python build.py stills upi-behind-the-scan
    python build.py video upi-behind-the-scan

Or set the local dashboard's Engine path to this file:

    <repo>\projects\upi-behind-the-scan\render\build.py

The dashboard's Check and Video actions will then use this project's Canvas renderer. This Engine setting is global in the existing Flask app, so other projects without a render/ scene package will not use this adapter correctly. For that reason, running the adapter directly is the safer option until the dashboard supports per-project renderers.

## Timing and current limitations

- Shot boundaries are estimated by distributing the actual recording duration according to each storyboard scene's script word count. This is a first-pass timing map, not forced alignment.
- The project still needs your WAV recording. Final scene timing must be reviewed against your real pauses and delivery.
- No subtitles are burned in because the current Hindi aligner has not been validated. Add subtitles only after checking sentence/word timings against the recording.
- No music or sound effects are mixed yet; the narration remains the sole audio track.
- The visuals are code-drawn explanatory illustrations. They are not archival footage or real bank interfaces.
- The full 8–9 minute render may take time because the browser captures frames sequentially. Use the PNG scene preview first.

## Files

- index.html — fixed-size browser canvas.
- scene.js — 16 deterministic motion scenes and drawing primitives.
- render.mjs — Playwright frame capture and FFmpeg mux.
- build.py — small command adapter for the local Flask studio.
