#!/usr/bin/env python
"""Generate short VoxCPM2 voice-design auditions for the UPI explainer."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

PROJECT = Path(__file__).resolve().parents[1]
AUDIO_PREVIEWS = PROJECT / "audio" / "previews" / "voxcpm2"
SCRIPT_PATH = PROJECT / "script-tts.json"
MODEL_ID = "openbmb/VoxCPM2"

VOICE_DESIGNS = {
    "male": (
        "(A warm, mature Indian male documentary narrator. "
        "Neutral North Indian Hindi accent, natural conversational Hinglish, "
        "clear diction, medium-slow pace, confident and curious delivery. "
        "Use subtle emphasis on questions. Do not sound like a newsreader.)"
    ),
    "female": (
        "(A warm, mature Indian female documentary narrator. "
        "Neutral North Indian Hindi accent, natural conversational Hinglish, "
        "clear diction, medium-slow pace, confident and curious delivery. "
        "Use subtle emphasis on questions. Do not sound like a newsreader.)"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate CPU-based VoxCPM2 auditions from the UPI script."
    )
    parser.add_argument("--voice", choices=("male", "female", "both"), default="both")
    parser.add_argument("--lines", type=int, default=8)
    parser.add_argument("--timesteps", type=int, default=10)
    parser.add_argument("--cfg", type=float, default=1.6)
    parser.add_argument("--model", default=MODEL_ID)
    return parser.parse_args()


def load_excerpt(line_count: int) -> str:
    if not SCRIPT_PATH.is_file():
        raise FileNotFoundError(f"Missing TTS script: {SCRIPT_PATH}")
    lines = json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))
    if not isinstance(lines, list) or not lines:
        raise ValueError("script-tts.json must contain a non-empty JSON array.")
    if line_count < 1 or line_count > len(lines):
        raise ValueError(f"--lines must be between 1 and {len(lines)}.")
    selected = lines[:line_count]
    if any(not isinstance(line, str) or not line.strip() for line in selected):
        raise ValueError("The selected TTS script excerpt contains an empty line.")
    # One paragraph preserves prosody across sentence boundaries.
    return " ".join(line.strip() for line in selected)


def to_numpy(audio: Any) -> np.ndarray:
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    result = np.asarray(audio, dtype=np.float32).squeeze()
    if result.ndim != 1 or result.size == 0:
        raise RuntimeError("VoxCPM2 returned empty or non-mono audio.")
    if not np.isfinite(result).all():
        raise RuntimeError("VoxCPM2 returned NaN or infinite audio samples.")
    return np.clip(result, -1.0, 1.0)


def main() -> int:
    args = parse_args()
    if not 1 <= args.timesteps <= 30:
        raise ValueError("--timesteps must be between 1 and 30.")
    if not 1.0 <= args.cfg <= 3.0:
        raise ValueError("--cfg must be between 1.0 and 3.0.")

    try:
        import torch
        from voxcpm import VoxCPM
    except ImportError as exc:
        raise RuntimeError(
            "VoxCPM2 dependencies are missing. Run setup_voxcpm2.bat first."
        ) from exc

    # Leave some CPU capacity available to Windows while synthesizing.
    cpu_threads = max(1, min(10, (os.cpu_count() or 8) - 2))
    torch.set_num_threads(cpu_threads)
    try:
        torch.set_num_interop_threads(4)
    except RuntimeError:
        pass

    excerpt = load_excerpt(args.lines)
    voices = ("male", "female") if args.voice == "both" else (args.voice,)
    AUDIO_PREVIEWS.mkdir(parents=True, exist_ok=True)

    print(f"Model: {args.model}")
    print("Runtime: VoxCPM2 / PyTorch CPU (no CUDA, no torch.compile)")
    print(f"CPU threads: {cpu_threads}")
    print(f"Excerpt: first {args.lines} script lines, one paragraph")
    print("Loading the model; first run downloads several GB of model weights...")

    model = VoxCPM.from_pretrained(
        args.model,
        device="cpu",
        optimize=False,
        load_denoiser=False,
    )

    metadata: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "runtime": "PyTorch CPU",
        "device": "cpu",
        "optimize": False,
        "inference_timesteps": args.timesteps,
        "cfg_value": args.cfg,
        "excerpt_lines": args.lines,
        "excerpt_text": excerpt,
        "outputs": [],
        "note": (
            "Audition only. This script does not create native sentence or word "
            "timing sidecars. Align and review separately before final rendering."
        ),
    }

    for voice in voices:
        prompt = VOICE_DESIGNS[voice]
        print(f"\nGenerating {voice} voice design...")
        audio = model.generate(
            text=f"{prompt}{excerpt}",
            cfg_value=args.cfg,
            inference_timesteps=args.timesteps,
            normalize=True,
            retry_badcase=True,
        )
        samples = to_numpy(audio)
        sample_rate = int(model.tts_model.sample_rate)
        destination = AUDIO_PREVIEWS / f"voxcpm2-{voice}.wav"
        sf.write(destination, samples, sample_rate, subtype="PCM_16")

        duration = round(samples.size / sample_rate, 3)
        metadata["outputs"].append({
            "voice": voice,
            "voice_description": prompt,
            "file": str(destination.relative_to(PROJECT)),
            "sample_rate_hz": sample_rate,
            "duration_seconds": duration,
            "sample_count": int(samples.size),
        })
        print(f"Saved: {destination}")
        print(f"Duration: {duration:.1f}s at {sample_rate} Hz")

    metadata_path = AUDIO_PREVIEWS / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nMetadata: {metadata_path}")
    print("\nAudition only: Kokoro production narration has not been changed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"VoxCPM2 audition failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
