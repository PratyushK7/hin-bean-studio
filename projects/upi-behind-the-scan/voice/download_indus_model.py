#!/usr/bin/env python
"""Download only the files required by Indus Pocket TTS."""

from pathlib import Path
from huggingface_hub import snapshot_download

VOICE_DIR = Path(__file__).resolve().parent
DESTINATION = VOICE_DIR / "indus-pocket-tts-model"

required = [
    "config.yaml",
    "model.safetensors",
    "tokenizer.model",
    "speak.py",
    "LICENSE.md",
    "README.md",
    "normalizer/**",
    "voices/**",
]

print("Downloading Indus-Labs/indus-pocket-tts to:")
print(DESTINATION)
snapshot_download(
    repo_id="Indus-Labs/indus-pocket-tts",
    local_dir=str(DESTINATION),
    allow_patterns=required,
)
print("Model files downloaded.")
