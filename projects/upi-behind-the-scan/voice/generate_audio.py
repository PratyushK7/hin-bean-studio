#!/usr/bin/env python
"""Local Hindi speech synthesis. Writes narration.wav and sentence/word timing sidecars."""

from __future__ import annotations
import argparse
import json
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mediapipe as mp
import numpy as np

VOICE_IDS = ("hf_alpha", "hf_beta", "hm_omega", "hm_psi")
PROJECT = Path(__file__).resolve().parents[1]
VOICE_DIR = Path(__file__).resolve().parent
MODEL_DEFAULT = VOICE_DIR / "models" / "kokoro_int8_fp16.litertlm"
AUDIO = PROJECT / "audio"


def parse_args():
    p = argparse.ArgumentParser(description="Generate Hindi narration with local Kokoro-82M.")
    p.add_argument("--voice", choices=VOICE_IDS, default="hf_alpha")
    p.add_argument("--preview-all", action="store_true", help="Audition all four Hindi voices.")
    p.add_argument("--limit", type=int, default=None, help="Synthesize only the first N sentences.")
    p.add_argument("--paragraph", action="store_true", help="Join a limited excerpt into one paragraph for a fair TTS comparison.")
    p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--pause", type=float, default=0.18)
    p.add_argument("--question-pause", type=float, default=0.30)
    p.add_argument("--out", type=Path, default=None, help="Optional WAV path relative to project root.")
    p.add_argument("--model", type=Path, default=MODEL_DEFAULT)
    return p.parse_args()


def project_path(value: Path) -> Path:
    return value.resolve() if value.is_absolute() else (PROJECT / value).resolve()


def load_script():
    original = json.loads((PROJECT / "script.json").read_text(encoding="utf-8"))
    spoken = json.loads((PROJECT / "script-tts.json").read_text(encoding="utf-8"))
    if not isinstance(original, list) or not isinstance(spoken, list):
        raise ValueError("Both script files must contain JSON arrays.")
    if len(original) != len(spoken):
        raise ValueError("script.json and script-tts.json have different line counts.")
    if any(not isinstance(s, str) or not s.strip() for s in spoken):
        raise ValueError("The spoken script contains an empty or invalid line.")
    return spoken


def write_wav(path: Path, audio: np.ndarray, rate: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(pcm.tobytes())


def make_tts(model: Path, voice: str, speed: float, cache: Path):
    if not model.is_file():
        raise FileNotFoundError("Kokoro model not found: " + str(model) + ". Run setup.bat first.")
    options = mp.tasks.audio.TextToSpeechOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path=str(model),
            delegate=mp.tasks.BaseOptions.Delegate.CPU,
        ),
        default_voice_id=voice,
        speaking_rate=speed,
        cache_directory=str(cache),
    )
    return mp.tasks.audio.TextToSpeech.create_from_options(options)


def speak_lines(tts: Any, lines: list[str], voice: str, pause: float, question_pause: float):
    chunks = []
    sentence_rows = []
    word_rows = []
    sample_rate = None
    cursor = 0

    for index, text in enumerate(lines):
        result = tts.synthesize(text, voice_id=voice)
        rate = int(result.sample_rate_hz)
        if sample_rate is None:
            sample_rate = rate
        if rate != sample_rate:
            raise RuntimeError("The TTS sample rate changed during synthesis.")
        samples = np.asarray(result.samples, dtype=np.float32).reshape(-1)
        if samples.size == 0:
            raise RuntimeError("No audio returned for sentence " + str(index + 1))

        start = cursor / rate
        end = (cursor + len(samples)) / rate
        sentence_rows.append({
            "line": index, "s": round(start, 4), "e": round(end, 4), "text": text
        })

        for word in (getattr(result, "word_timestamps", None) or []):
            word_rows.append({
                "line": index,
                "word": str(word.word),
                "start_char": int(word.start_char),
                "end_char": int(word.end_char),
                "s": round(start + float(word.start_sec), 4),
                "e": round(start + float(word.end_sec), 4),
            })

        chunks.append(samples)
        cursor += len(samples)
        gap = question_pause if text.rstrip().endswith(("?", "!", "…")) else pause
        if index < len(lines) - 1 and gap:
            silence = np.zeros(int(gap * rate), dtype=np.float32)
            chunks.append(silence)
            cursor += len(silence)

        if (index + 1) % 5 == 0 or index + 1 == len(lines):
            print("Synthesized " + str(index + 1) + "/" + str(len(lines)) + " sentences (" + voice + ")")

    if sample_rate is None:
        raise RuntimeError("No audio was synthesized.")
    chunks.append(np.zeros(int(0.65 * sample_rate), dtype=np.float32))
    return np.concatenate(chunks), sentence_rows, word_rows, sample_rate


def main():
    args = parse_args()
    if not 0.1 < args.speed <= 4.0:
        raise ValueError("--speed must be greater than 0 and at most 4.")
    if args.pause < 0 or args.question_pause < 0:
        raise ValueError("Pause durations cannot be negative.")
    lines = load_script()
    if args.paragraph and args.limit is None:
        raise ValueError("--paragraph is intended for short auditions; provide --limit N.")

    if args.preview_all:
        count = args.limit or 4
        if count < 1:
            raise ValueError("--limit must be positive.")
        chosen_lines = lines[:count]
        voices = list(VOICE_IDS)
        if args.out:
            raise ValueError("--out cannot be combined with --preview-all.")
    else:
        chosen_lines = lines[:args.limit] if args.limit else lines
        if not chosen_lines:
            raise ValueError("--limit must be positive.")
        voices = [args.voice]
        if args.paragraph:
            chosen_lines = [" ".join(chosen_lines)]

    model = project_path(args.model)
    cache = VOICE_DIR / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)

    print("Model: " + str(model))
    print("Runtime: MediaPipe Text-to-Speech + Kokoro-82M, CPU delegate")
    print("Mode: " + ("four voice audition" if args.preview_all else "full script" if len(chosen_lines) == len(lines) else "short preview"))

    with make_tts(model, voices[0], args.speed, cache) as tts:
        for voice in voices:
            audio, sentences, words, rate = speak_lines(
                tts, chosen_lines, voice, args.pause, args.question_pause
            )
            if args.preview_all:
                destination = AUDIO / "previews" / (voice + ".wav")
            elif len(chosen_lines) < len(lines):
                suffix = "-paragraph-preview.wav" if args.paragraph else "-preview.wav"
                destination = AUDIO / "previews" / (voice + suffix)
            elif args.out:
                destination = project_path(args.out)
            else:
                destination = AUDIO / "hindi-voice.wav"
            write_wav(destination, audio, rate)
            print("Saved: " + str(destination))

            if not args.preview_all and len(chosen_lines) == len(lines):
                (AUDIO / "sentences.json").write_text(
                    json.dumps(sentences, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                (AUDIO / "words.json").write_text(
                    json.dumps(words, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                manifest = {
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                    "engine": "MediaPipe Text-to-Speech + Kokoro-82M",
                    "voice": voice,
                    "sample_rate_hz": rate,
                    "duration_seconds": round(len(audio) / rate, 3),
                    "sentence_count": len(sentences),
                    "word_timestamp_count": len(words),
                    "model": model.name,
                    "delegate": "CPU",
                }
                (AUDIO / "manifest.json").write_text(
                    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                print("Timing sidecars: " + str(len(sentences)) + " sentences; " + str(len(words)) + " words")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Audio generation failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
