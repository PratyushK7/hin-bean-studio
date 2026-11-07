@echo off
setlocal
cd /d "%~dp0"

echo Indus Pocket TTS - local CPU setup
echo Separate environment: .venv-indus-tts
echo Model weights: approximately 440 MB, plus runtime dependencies.
echo.

if not exist ".venv-indus-tts\Scripts\python.exe" (
  echo [1/4] Creating Python 3.11 environment...
  py -3.11 -m venv .venv-indus-tts
  if errorlevel 1 goto :failed
) else (
  echo [1/4] Reusing .venv-indus-tts.
)

echo.
echo [2/4] Installing CPU-only PyTorch...
".venv-indus-tts\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
".venv-indus-tts\Scripts\python.exe" -m pip install torch --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto :failed

echo.
echo [3/4] Installing the pinned Pocket-TTS runtime...
".venv-indus-tts\Scripts\python.exe" -m pip install "pocket-tts @ git+https://github.com/kyutai-labs/pocket-tts@0c2db3b" huggingface_hub soundfile numpy
if errorlevel 1 goto :failed

echo.
echo [4/4] Downloading Indus Hindi/Hinglish model and voice...
".venv-indus-tts\Scripts\python.exe" download_indus_model.py
if errorlevel 1 goto :failed

echo.
echo Verifying imports...
".venv-indus-tts\Scripts\python.exe" -c "import torch; import pocket_tts; import soundfile; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available()); print('Pocket-TTS: OK')"
if errorlevel 1 goto :failed

echo.
echo Setup complete. Run run_indus_pocket_tts.bat
echo.
pause
exit /b 0

:failed
echo.
echo Setup failed. Keep the full error output.
pause
exit /b 1
