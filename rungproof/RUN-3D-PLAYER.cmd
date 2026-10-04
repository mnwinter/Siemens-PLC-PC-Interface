@echo off
setlocal
cd /d "%~dp0"
if exist "build\.venv-rungproof\Scripts\python.exe" (
  "build\.venv-rungproof\Scripts\python.exe" -m tools.rungproof_native %*
) else (
  py -3 -m tools.rungproof_native %*
)
if errorlevel 1 pause
