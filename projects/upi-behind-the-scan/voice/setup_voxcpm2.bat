@echo off
setlocal
cd /d "%~dp0"

echo VoxCPM2 local CPU audition setup
echo This installs into .venv-voxcpm2 and does not touch the Kokoro environment.
echo.

if not exist ".venv-voxcpm2\Scripts\python.exe" (
  echo [1/4] Creating Python 3.11 virtual environment...
  py -3.11 -m venv .venv-voxcpm2 >nul 2>nul
  if errorlevel 1 (
    echo Python 3.11 was not found. Trying Python 3.10...
    py -3.10 -m venv .venv-voxcpm2 >nul 2>nul
  )
  if errorlevel 1 (
    echo Python 3.10 was not found. Trying Python 3.12...
    py -3.12 -m venv .venv-voxcpm2 >nul 2>nul
  )
  if errorlevel 1 (
    echo.
    echo Could not create the environment.
    echo Install Python 3.10, 3.11 or 3.12 and enable the Python Launcher.
    goto :failed
  )
) else (
  echo [1/4] Reusing existing .venv-voxcpm2 environment.
)

set "HF_HOME=%~dp0voxcpm2-models"

echo.
echo [2/4] Updating pip...
".venv-voxcpm2\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :failed

echo.
echo [3/4] Installing CPU-only PyTorch...
".venv-voxcpm2\Scripts\python.exe" -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto :failed

echo.
echo [4/4] Installing VoxCPM2 and its dependencies...
".venv-voxcpm2\Scripts\python.exe" -m pip install voxcpm
if errorlevel 1 goto :failed

echo.
echo Verifying imports...
".venv-voxcpm2\Scripts\python.exe" -c "import torch; from voxcpm import VoxCPM; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('VoxCPM import: OK')"
if errorlevel 1 goto :failed

echo.
echo Setup complete.
echo Run run_voxcpm2_audition.bat to download the model and generate two short samples.
echo The first run downloads several GB of model files and CPU synthesis may be slow.
echo.
pause
exit /b 0

:failed
echo.
echo Setup failed. Keep the full error text; do not remove the existing Kokoro environment.
pause
exit /b 1
