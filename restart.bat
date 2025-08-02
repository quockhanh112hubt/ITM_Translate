@echo off
title ITM Translate - Restart Process (Development)
echo [INFO] ITM Translate restart process started (Development Mode)...

REM Wait for current application to close
echo [INFO] Waiting for application to close...
timeout /t 3 /nobreak >nul

REM Check if Python process is still running and wait
:wait_close
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "ITM_Translate" >NUL
if "%ERRORLEVEL%"=="0" (
    echo [WAIT] Python process still running, waiting...
    timeout /t 2 /nobreak >nul
    goto wait_close
)

echo [INFO] Application closed successfully
echo [INFO] Starting ITM Translate (Development mode)...

REM Start new application
cd /d "E:\GitHub\ITM_Translate"
"e:\GitHub\ITM_Translate\.venv\Scripts\python.exe" "E:\GitHub\ITM_Translate\ITM_Translate.py"

if "%ERRORLEVEL%"=="0" (
    echo [SUCCESS] ITM Translate restarted successfully
) else (
    echo [ERROR] Failed to restart ITM Translate
)

REM Self-delete this batch file
echo [INFO] Cleaning up restart batch file...
timeout /t 2 /nobreak >nul
del "%~f0"
