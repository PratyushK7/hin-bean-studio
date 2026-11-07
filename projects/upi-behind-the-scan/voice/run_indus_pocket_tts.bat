@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv-indus-tts\Scripts\python.exe" (
  echo Run setup_indus_pocket_tts.bat first.
  exit /b 1
)

".venv-indus-tts\Scripts\python.exe" generate_indus_audition.py %*
if errorlevel 1 (
  echo.
  echo Indus Pocket TTS audition failed. Keep the error output.
  pause
  exit /b 1
)

echo.
echo Audition folder: ..\audio\previews\indus-pocket-tts
pause
