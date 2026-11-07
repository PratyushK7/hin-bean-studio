#!/usr/bin/env python
"""Create a short Indus Pocket TTS Hindi/Hinglish audition on CPU."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

PROJECT = Path(__file__).resolve().parents[1]
VOICE_DIR = Path(__file__).resolve().parent
MODEL_DIR = VOICE_DIR / "indus-pocket-tts-model"
SCRIPT_PATH = PROJECT / "script-tts.json"
OUTPUT_DIR = PROJECT / "audio" / "previews" / "indus-pocket-tts"
MODEL_ID = "Indus-Labs/indus-pocket-tts"
MODEL_LICENSE = "CC-BY-4.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a short Hindi/Hinglish CPU TTS audition."
    )
    parser.add_argument("--lines", type=int, default=8)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument(
        "--no-int8",
        action="store_true",
        help="Use full precision instead of the faster int8 weights.",
    )
    return parser.parse_args()


def load_script(lines_count: int) -> str:
    if not SCRIPT_PATH.is_file():
        raise FileNotFoundError(f"Missing script: {SCRIPT_PATH}")
    lines = json.loads(SCRIPT_PATH.read_text(encoding="utf-8"))
    if not isinstance(lines, list) or not lines:
        raise ValueError("script-tts.json must contain a non-empty JSON array.")
    if not 1 <= lines_count <= len(lines):
        raise ValueError(f"--lines must be between 1 and {len(lines)}.")
    selected = lines[:lines_count]
    if any(not isinstance(line, str) or not line.strip() for line in selected):
        raise ValueError("Selected lines contain empty or invalid text.")
    return " ".join(line.strip() for line in selected)


def import_speaker() -> Any:
    speak_path = MODEL_DIR / "speak.py"
    if not speak_path.is_file():
        raise FileNotFoundError(
            f"Indus model files are missing from {MODEL_DIR}. "
            "Run setup_indus_pocket_tts.bat first."
        )
    spec = importlib.util.spec_from_file_location("indus_pocket_speak", speak_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the Indus Pocket TTS speak.py module.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def to_float_array(chunk: Any) -> np.ndarray:
    if hasattr(chunk, "detach"):
        chunk = chunk.detach().cpu().numpy()
    array = np.asarray(chunk, dtype=np.float32).reshape(-1)
    if array.size == 0:
        return array
    if not np.isfinite(array).all():
        raise RuntimeError("TTS returned NaN or infinite audio.")
    return np.clip(array, -1.0, 1.0)


def main() -> int:
    args = parse_args()
    if args.threads < 1 or args.threads > 8:
        raise ValueError("--threads must be between 1 and 8.")

    text = load_script(args.lines)
    speak = import_speaker()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    int8 = not args.no_int8
    print(f"Model: {MODEL_ID}")
    print("Runtime: Pocket-TTS / CPU")
    print(f"Quantization: {'int8' if int8 else 'full precision'}")
    print(f"Threads: {args.threads}")
    print(f"Excerpt: first {args.lines} script lines, one paragraph")
    print("Loading model and Inaya voice...")

    load_started = time.perf_counter()
    model, voice = speak.load(int8=int8, threads=args.threads)
    load_seconds = time.perf_counter() - load_started
    print(f"Model ready in {load_seconds:.1f}s. Generating audio...")

    chunks: list[np.ndarray] = []
    first_chunk_seconds: float | None = None
    synthesis_started = time.perf_counter()

    for chunk in speak.stream(model, voice, text):
        if first_chunk_seconds is None:
            first_chunk_seconds = time.perf_counter() - synthesis_started
        array = to_float_array(chunk)
        if array.size:
            chunks.append(array)

    synthesis_seconds = time.perf_counter() - synthesis_started
    if not chunks:
        raise RuntimeError("Pocket TTS did not return any audio chunks.")

    samples = np.concatenate(chunks)
    sample_rate = int(speak.SAMPLE_RATE)
    duration = samples.size / sample_rate
    output = OUTPUT_DIR / "indus-pocket-tts-hinglish.wav"
    sf.write(output, samples, sample_rate, subtype="PCM_16")

    realtime_factor = duration / synthesis_seconds if synthesis_seconds > 0 else 0.0
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID,
        "model_license": MODEL_LICENSE,
        "voice": "Inaya (single bundled female voice)",
        "runtime": "Pocket-TTS / CPU",
        "quantization": "int8" if int8 else "full precision",
        "threads": args.threads,
        "excerpt_lines": args.lines,
        "excerpt_text": text,
        "sample_rate_hz": sample_rate,
        "duration_seconds": round(duration, 3),
        "model_load_seconds": round(load_seconds, 3),
        "synthesis_seconds": round(synthesis_seconds, 3),
        "first_audio_ms": round((first_chunk_seconds or 0.0) * 1000, 2),
        "realtime_factor": round(realtime_factor, 3),
        "output": str(output.relative_to(PROJECT)),
        "attribution": (
            "Indus Pocket TTS by Indus AI, based on Kyutai Pocket TTS. "
            "Model weights CC-BY-4.0; inference scripts MIT; runtime MIT."
        ),
        "limitations": (
            "One voice only. The model is intended for conversational Hindi/Hinglish; "
            "long technical and descriptive narration may be less natural. "
            "Review the sample before considering full-video use."
        ),
    }
    (OUTPUT_DIR / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nSaved: {output}")
    print(f"Audio length: {duration:.1f}s")
    print(f"Model load: {load_seconds:.1f}s")
    print(f"Synthesis: {synthesis_seconds:.1f}s")
    print(f"Speed: {realtime_factor:.2f}x real-time")
    print("This is an audition only; the production WAV and renderer are unchanged.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Indus Pocket TTS audition failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
