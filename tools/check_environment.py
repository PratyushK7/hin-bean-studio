"""Check local prerequisites for Hindi Explainer Studio without modifying the system."""
from __future__ import annotations
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.json"
HOME_ENGINE = Path.home() / ".claude" / "skills" / "line-boil" / "engine" / "build.py"

def main() -> int:
    cfg = {}
    if CONFIG.exists():
        try:
            cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"FAIL config.json: {exc}")
    checks: list[tuple[str, bool, str]] = []
    checks.append(("Python >= 3.10", sys.version_info >= (3, 10), sys.version.split()[0]))
    for name in ("node", "ffmpeg", "ffprobe", "claude"):
        path = shutil.which(name)
        checks.append((name, bool(path), path or "not on PATH"))
    for module in ("flask", "openpyxl", "googleapiclient", "google_auth_oauthlib", "yt_dlp"):
        checks.append((f"Python module {module}", importlib.util.find_spec(module) is not None, "installed" if importlib.util.find_spec(module) else "not installed"))
    engine = Path(cfg.get("engine") or HOME_ENGINE)
    checks.append(("Renderer build.py", engine.is_file(), str(engine)))
    projects = Path(cfg.get("projects_dir") or ROOT / "projects")
    checks.append(("Projects directory", projects.exists() or projects.parent.exists(), str(projects)))
    secrets = ROOT / "tools" / ".secrets"
    checks.append(("YouTube OAuth client (optional until upload)", (secrets / "client_secret.json").is_file(), "present" if (secrets / "client_secret.json").is_file() else "not configured"))
    for label, ok, detail in checks:
        print(f"{'OK  ' if ok else 'MISS'} {label}: {detail}")
    missing = [label for label, ok, _ in checks if not ok]
    print("\nHindi-specific checks still require a manual smoke test: Devanagari font shaping, Hindi voice quality and Hindi speech alignment.")
    return 1 if missing else 0

if __name__ == "__main__":
    raise SystemExit(main())
