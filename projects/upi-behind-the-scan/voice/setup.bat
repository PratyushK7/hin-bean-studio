@echo off
setlocal
cd /d "%~dp0"

echo [1/3] Creating an isolated Python environment...
if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -m venv .venv
  ) else (
    python -m venv .venv
  )
  if errorlevel 1 goto :failed
)

echo [2/3] Installing local TTS dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
".venv\Scripts\python.exe" -m pip install "mediapipe>=1.2.0" "huggingface_hub>=0.30" "numpy>=1.26,<3"
if errorlevel 1 goto :failed

echo [3/3] Downloading Kokoro Hindi voices (about 295 MB)...
".venv\Scripts\python.exe" download_model.py
if errorlevel 1 goto :failed

echo.
echo Setup complete.
echo Run: .venv\Scripts\python.exe generate_audio.py --preview-all --limit 4
echo.
pause
exit /b 0

:failed
echo.
echo Audio setup failed. Check the Python and package errors above.
pause
exit /b 1
