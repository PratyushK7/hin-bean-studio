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


## VoxCPM2 comparison audition (experimental CPU path)

Kokoro remains the current production default. VoxCPM2 is added as a separate A/B experiment so a failed or slow install cannot break the existing voice environment.

### Hardware note for this PC

The official VoxCPM2 acceleration path is NVIDIA CUDA. The Radeon RX 6700 XT is not a CUDA device, so this setup deliberately installs CPU-only PyTorch and forces CPU inference with optimization disabled. VoxCPM2 supports CPU inference, but the project FAQ warns that it is slow. The 2B model requires several GB of disk space; its published reference is about 8 GB of VRAM for the NVIDIA GPU path. Do not expect GPU acceleration on the RX 6700 XT in this Windows setup.

Official references:
- https://voxcpm.readthedocs.io/en/latest/quickstart.html
- https://voxcpm.readthedocs.io/en/latest/installation.html
- https://voxcpm.readthedocs.io/en/latest/faq.html
- https://voxcpm.readthedocs.io/en/latest/usage_guide.html

### Install

From this voice folder:

    setup_voxcpm2.bat

Use Python 3.10, 3.11 or 3.12. The setup creates a separate .venv-voxcpm2 environment, installs CPU-only PyTorch, and installs VoxCPM2 dependencies. It does not change or reuse the existing .venv used by Kokoro.

### Generate the A/B samples

    run_voxcpm2_audition.bat

The first run downloads the model weights (several GB) into voice/voxcpm2-models/. It then creates a male and female voice-design sample from the same first eight lines of script-tts.json, as one continuous paragraph.

Output:

    projects/upi-behind-the-scan/audio/previews/voxcpm2/
        voxcpm2-male.wav
        voxcpm2-female.wav
        metadata.json

To generate only one voice or change the excerpt length:

    run_voxcpm2_audition.bat --voice male
    run_voxcpm2_audition.bat --voice female
    run_voxcpm2_audition.bat --lines 10

The script uses a restrained documentary-style voice description. The installed PyPI 2.0.3 runtime does not expose fixed-seed generation, so repeated runs may vary slightly; listen before selecting one.

### Compare with Kokoro

Generate the same eight opening lines with the existing Kokoro voice, as one paragraph:

    .venv\Scripts\python.exe generate_audio.py --voice hf_alpha --limit 8 --paragraph

Kokoro paragraph output:

    projects/upi-behind-the-scan/audio/previews/hf_alpha-paragraph-preview.wav

VoxCPM2 outputs are under audio/previews/voxcpm2/.

For an additional comparison, generate Kokoro with its original sentence-by-sentence behavior by omitting --paragraph. That output is hf_alpha-preview.wav. Comparing the two Kokoro samples helps show whether sentence-by-sentence chunking is contributing to the less-natural delivery.

### Important limitations

- This is an audition only; it does not overwrite audio/hindi-voice.wav or change the renderer.
- VoxCPM2 is generated as one paragraph to let the model carry intonation across sentence boundaries. Kokoro's current script emits one sentence at a time, so the comparison tests both model quality and the effect of paragraph-level generation.
- This audition script does not create sentence or word timing sidecars. If VoxCPM2 is selected, add a validated alignment pass before using its narration in the final video renderer.
- Do not run full-script synthesis on CPU until the short sample's quality and generation time have been assessed.
- If Windows installation fails, retain the complete error output. VoxCPM2's official FAQ documents Windows Triton issues; this setup disables torch.compile to avoid that path.


## Fast CPU alternative: Indus Pocket TTS (Hindi/Hinglish)

VoxCPM2 is a 2B model and is not practical on this PC's CPU-only path. Indus Pocket TTS is a much smaller 110M-parameter Hindi/Hinglish model with int8 quantization and Windows CPU support. The model card reports 6.3x real-time on an AMD EPYC test server; this is not a benchmark for this PC, so the local script reports its actual measured synthesis speed.

Model card: https://huggingface.co/Indus-Labs/indus-pocket-tts

### Trade-offs to know

- It has one bundled female voice, Inaya; no built-in male voice or voice cloning.
- It is trained primarily on conversational Hindi/Hinglish and short spoken customer-service lines.
- The model publisher lists literary/descriptive prose and long technical sentences as weaker cases. This is relevant to an educational explainer, so listen to the sample before using it for a full video.
- Hindi words should be in Devanagari; Romanised Hindi is read as English. The UPI script-tts.json is already Devanagari with selected English technical terms.
- The model weights are CC-BY-4.0. Include attribution when publishing generated audio. The upstream inference scripts and runtime are MIT; see the model card for the complete component licences.

### Install on Windows

From this voice folder:

    setup_indus_pocket_tts.bat

It creates .venv-indus-tts, installs CPU-only PyTorch and the pinned Pocket-TTS runtime, then downloads the approximately 440 MB model files into voice/indus-pocket-tts-model/. It does not modify the Kokoro or VoxCPM2 environments.

### Generate the short audition

    run_indus_pocket_tts.bat

The first eight script lines are joined into one paragraph. The default uses int8 weights and two CPU threads. The generator reports model-load time and measured synthesis real-time factor.

Output:

    projects/upi-behind-the-scan/audio/previews/indus-pocket-tts/
        indus-pocket-tts-hinglish.wav
        metadata.json

Optional settings:

    run_indus_pocket_tts.bat --lines 12
    run_indus_pocket_tts.bat --threads 1
    run_indus_pocket_tts.bat --no-int8

Do not replace audio/hindi-voice.wav or use this audition as final video narration until the complete UPI script has been listened to. It does not currently generate sentence timing sidecars.
