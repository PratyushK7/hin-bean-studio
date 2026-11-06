"""Thin adapter for Hindi Explainer Studio's local Flask dashboard.

Configure this file as the project's Engine path only when you want the
local dashboard's Check and Video actions to use this standalone Canvas renderer.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

RENDER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = RENDER_DIR.parent
PROJECT_SLUG = PROJECT_DIR.name
NODE_SCRIPT = RENDER_DIR / "render.mjs"
AUDIO = PROJECT_DIR / "audio" / "hindi-voice.wav"
OUTPUT = PROJECT_DIR / f"{PROJECT_SLUG}.mp4"


def run(command: list[str]) -> int:
    print("+ " + subprocess.list2cmdline(command), flush=True)
    result = subprocess.run(command, cwd=RENDER_DIR)
    return result.returncode


def check() -> int:
    problems = []
    for binary in ("node", "ffmpeg", "ffprobe"):
        path = shutil.which(binary)
        print(f"{binary}: {path or 'NOT FOUND'}")
        if not path:
            problems.append(f"Install {binary} and add it to PATH.")
    if not NODE_SCRIPT.is_file():
        problems.append(f"Missing {NODE_SCRIPT}")
    if not (RENDER_DIR / "node_modules" / "playwright").exists():
        problems.append("Run npm install from the render folder.")
    print(f"Voice recording: {'present' if AUDIO.is_file() else 'not yet present'} ({AUDIO})")
    if problems:
        for problem in problems:
            print("ERROR: " + problem)
        return 1
    print("Canvas renderer dependencies are present.")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python build.py check|stills|video <project-slug>")
        return 2

    action = sys.argv[1].lower()
    slug = sys.argv[2] if len(sys.argv) > 2 else PROJECT_SLUG
    if slug != PROJECT_SLUG:
        print(f"This adapter belongs to {PROJECT_SLUG}, not {slug}.")
        return 2

    if action == "check":
        return check()
    if action == "stills":
        if not shutil.which("node"):
            print("ERROR: Node.js is not on PATH.")
            return 1
        return run(["node", str(NODE_SCRIPT), "--stills", "--out", str(RENDER_DIR / "stills")])
    if action == "video":
        status = check()
        if status:
            return status
        if not AUDIO.is_file():
            print(f"ERROR: Record your Hinglish narration to {AUDIO}")
            return 1
        return run([
            "node", str(NODE_SCRIPT),
            "--audio", str(AUDIO),
            "--out", str(OUTPUT),
        ])

    print("Supported actions: check, stills, video")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
