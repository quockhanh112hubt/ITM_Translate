@echo off
title ITM Translate - Restart Process (Development)
echo.
echo ====================================
echo   ITM Translate Restart Process     
echo   Development Mode                   
echo ====================================
echo.

echo [INFO] Waiting for application to close...
timeout /t 3 /nobreak >nul

echo [INFO] Checking if Python processes are still running...
:check_process
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "ITM_Translate">NUL
if "%ERRORLEVEL%"=="0" (
    echo [WAIT] Python process still running, waiting...
    timeout /t 2 /nobreak >nul
    goto check_process
)

echo [INFO] Application closed successfully
echo [INFO] Starting ITM Translate (Development mode)...

cd /d "E:\GitHub\ITM_Translate"
"e:\GitHub\ITM_Translate\.venv\Scripts\python.exe" "E:\GitHub\ITM_Translate\ITM_Translate.py"

echo [SUCCESS] ITM Translate restarted successfully
echo [INFO] Cleaning up restart batch file...

timeout /t 2 /nobreak >nul
del "%~f0"
