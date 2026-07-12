@echo off
setlocal
cd /d "%~dp0"

echo Starting ATLAS by EWU...
echo.

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  start "ATLAS by EWU" py -3.12 -m uvicorn api.app:app --host 127.0.0.1 --port 8000
  goto opened
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  start "ATLAS by EWU" python -m uvicorn api.app:app --host 127.0.0.1 --port 8000
  goto opened
)

echo Python was not found on this computer.
echo Install Python 3.12, then run this file again.
pause
exit /b 1

:opened
timeout /t 3 /nobreak >nul
start http://127.0.0.1:8000
echo ATLAS is starting at http://127.0.0.1:8000
echo Keep the server window open while using ATLAS.
pause
