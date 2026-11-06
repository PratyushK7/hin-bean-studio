@echo off
rem Hindi Explainer Studio. Creates or refreshes the local Python environment.
cd /d "%~dp0"
set PYTHONUTF8=1
set BEAN_AUTORESTART=1
:run
if not exist ".venv\Scripts\python.exe" (
  echo Setting up Hindi Explainer Studio...
  python -m venv .venv || (echo Python 3.10+ is required. & pause & exit /b 1)
)
set REQHASH=
for /f %%h in ('certutil -hashfile requirements.txt MD5 ^| findstr /v ":"') do if not defined REQHASH set REQHASH=%%h
set OLDHASH=
if exist ".venv\req.hash" set /p OLDHASH=<".venv\req.hash"
if not "%REQHASH%"=="%OLDHASH%" (
  echo Installing Python dependencies...
  ".venv\Scripts\python.exe" -m pip install -q --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt || (echo Dependency installation failed. & pause & exit /b 1)
  >".venv\req.hash" echo %REQHASH%
)
".venv\Scripts\python.exe" app\server.py
if %errorlevel%==3 goto run
if errorlevel 1 pause
