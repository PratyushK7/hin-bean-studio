# Local Hindi narration

This folder adds a local narration stage to the UPI video. It follows the Bean Studio production pattern: create a sentence-by-sentence WAV on your PC, then render it with the local video pipeline. It uses Hindi Kokoro voices, not Bean Studio's English af_heart voice.

## Model

- Runtime: Google MediaPipe Text-to-Speech.
- Speech model: Kokoro-82M, LiteRT-LM bundle.
- Hindi voices: hf_alpha, hf_beta, hm_omega, hm_psi.
- Model file: kokoro_int8_fp16.litertlm (about 295 MB).
- Delegate: CPU. No CUDA setup is required.
- The model is downloaded once; speech synthesis then runs locally without a TTS API key.
- The model is Apache-2.0 licensed.

## Install on Windows

Open Command Prompt in this folder and run:

    setup.bat

It creates an isolated Python environment in voice/.venv, installs dependencies and downloads the model under voice/models/. It does not change the main Studio Python environment.

## Audition the voices

    .venv\Scripts\python.exe generate_audio.py --preview-all --limit 4

Four sample WAVs are written to the project's audio/previews folder. Listen to them and choose the most natural one. The voice IDs are:

- hf_alpha
- hf_beta
- hm_omega
- hm_psi

The original script.json remains Roman Hinglish. The separate script-tts.json contains a Devanagari pronunciation version with the same 83 sentence positions. This helps the Hindi phonemizer read Hindi words and acronyms. Check brand names, acronyms, amounts and English technical terms in the short voice auditions before generating the full narration.

## Generate the complete narration

Example:

    .venv\Scripts\python.exe generate_audio.py --voice hf_alpha

Replace hf_alpha with the voice you selected. The resulting file is:

    projects/upi-behind-the-scan/audio/hindi-voice.wav

A short sample can be generated without overwriting the full take:

    .venv\Scripts\python.exe generate_audio.py --voice hm_omega --limit 6

Pacing can be adjusted during synthesis:

    .venv\Scripts\python.exe generate_audio.py --voice hf_alpha --speed 0.96 --pause 0.20 --question-pause 0.34

## Output

- audio/hindi-voice.wav: final narration.
- audio/sentences.json: actual audio start/end times for all 83 sentences.
- audio/words.json: word timestamps returned by MediaPipe, if supplied by the model runtime.
- audio/manifest.json: model, voice, sample rate and duration metadata.
- audio/previews/: audition recordings.

## Render

After generating the WAV, open the renderer folder:

    cd ..\render
    npm run render -- --audio ..\audio\hindi-voice.wav --out ..\upi-behind-the-scan.mp4

The renderer uses sentence timings when audio/sentences.json is present. If you replace the generated narration with a separately recorded human voice, delete or regenerate sentences.json first; otherwise it will align the scenes to the previous generated take.

## Review before publishing

Listen to the whole narration and check UPI, NPCI, IMPS, PSP, PhonePe, Google Pay, remitter and beneficiary. Edit a mispronounced line in script-tts.json and regenerate. The saved word timestamps are machine-provided timing data, not human-verified subtitles.
