@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv-voxcpm2\Scripts\python.exe" (
  echo VoxCPM2 environment is missing. Run setup_voxcpm2.bat first.
  exit /b 1
)

set "HF_HOME=%~dp0voxcpm2-models"

".venv-voxcpm2\Scripts\python.exe" generate_voxcpm2_audition.py %*
if errorlevel 1 (
  echo.
  echo VoxCPM2 audition failed. Keep the error text for troubleshooting.
  pause
  exit /b 1
)

echo.
echo Auditions are in: ..\audio\previews\voxcpm2
pause
