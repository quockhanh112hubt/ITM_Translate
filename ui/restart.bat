@echo off
title ITM Translate - Restart Process
echo.
echo ================================
echo   ITM Translate Restart Process  
echo ================================
echo.

echo [INFO] Waiting for application to close...
timeout /t 3 /nobreak >nul

echo [INFO] Checking if application is still running...
:check_process
tasklist /FI "IMAGENAME eq ITM_Translate.exe" 2>NUL | find /I /N "ITM_Translate.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [WAIT] Application still running, waiting...
    timeout /t 2 /nobreak >nul
    goto check_process
)

echo [INFO] Application closed successfully
echo [INFO] Starting ITM Translate...

cd /d "E:\GitHub\ITM_Translate\ui"
start "" "E:\GitHub\ITM_Translate\ui\gui.py"

echo [SUCCESS] ITM Translate restarted successfully
echo [INFO] Cleaning up restart batch file...

(goto) 2>nul & del "%~f0"
