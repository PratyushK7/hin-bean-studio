# UPI: Aapke ₹20 ke Peeche Kaun Kaam Karta Hai?

- **Format:** 16:9 long-form explainer
- **Target runtime:** 8–9 minutes (final timing depends on the human recording)
- **Language:** Roman-script Hinglish
- **Narration:** Creator's own voice; no English TTS fallback
- **Visual direction:** Hybrid documentary — code-generated transaction diagrams, motion graphics, and carefully selected documentary context.

## Central question
Jab aap UPI se kisi ko paise bhejte ho, toh phone screen ke peeche kaunse systems milkar payment complete karte hain?

## Editorial thesis
UPI ek app ya simple digital wallet nahi hai. Common bank-linked UPI payment mein app interface hota hai; PSPs, NPCI ka routing layer, aur sender/receiver banks milkar transaction ko authenticate, route, debit aur credit karte hain.

## Status
- [x] Research and claim ledger
- [x] Hinglish narration draft
- [x] Storyboard and visual plan
- [x] Thumbnail and YouTube metadata
- [ ] Script approval
- [x] Local Hindi Kokoro TTS generator and Devanagari pronunciation script
- [ ] Listen to TTS voice previews and select a narration voice
- [ ] Generate and quality-check `audio/hindi-voice.wav`
- [ ] Hindi/Hinglish font and alignment smoke test
- [x] Standalone 16-scene Canvas implementation (local renderer)
- [ ] Install Playwright/Chromium locally and inspect the 16-scene PNG preview
- [ ] Render and quality review

## Important
The repo's original line-boil renderer is a configurable local dependency, not bundled here. To avoid inventing its unavailable drawing API, this project now includes a separate self-contained Canvas renderer under render/. It captures deterministic browser frames with Playwright and muxes your WAV narration using FFmpeg. The local renderer still needs npm dependencies and a Chromium install on your PC. Inspect the preview before full rendering; shot boundaries are estimated from script word counts and are not speech-aligned.

## Files
- `research.md`, `sources.md`, `claims.json`
- `script-hinglish.md`, `script.json`, `pronunciation.md`
- `storyboard.json`, `chapters.json`
- `thumbnail.md`, `youtube-metadata.md`, `recording-notes.md`

## Local renderer

See [render/README.md](render/README.md). It contains the 16 scene implementations, a local preview command and the FFmpeg render command. Generate local Hindi narration with voice/setup.bat and voice/generate_audio.py, or record your own Hinglish narration at audio/hindi-voice.wav. The TTS generator writes sentence and optional word timing sidecars; the renderer uses sentence timings when present.


## Local audio generation

This project follows Bean Studio's local-first narration pattern using Google MediaPipe Text-to-Speech with Kokoro-82M Hindi voices. It does not call an external TTS API.

From the project voice folder on Windows:

    setup.bat
    .venv\Scripts\python.exe generate_audio.py --preview-all --limit 4
    .venv\Scripts\python.exe generate_audio.py --voice hf_alpha

The setup downloads the CPU/GPU Kokoro model once (about 295 MB). Listen to the four short voice samples, choose one, then generate the full WAV. See voice/README.md for the full procedure.
