@echo off
echo ================================================
echo   ITM Translate - Installer Builder
echo ================================================

REM Set paths
set INNO_SETUP="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set PROJECT_DIR=%~dp0
set SETUP_SCRIPT=%PROJECT_DIR%installer\setup.iss
set OUTPUT_DIR=%PROJECT_DIR%installer\output

echo.
echo Checking requirements...

REM Check if Inno Setup is installed
if not exist %INNO_SETUP% (
    echo ❌ Inno Setup not found at %INNO_SETUP%
    echo Please install Inno Setup 6 from: https://jrsoftware.org/isinfo.php
    echo.
    pause
    exit /b 1
)

REM Check if exe exists
if not exist "%PROJECT_DIR%dist\ITM_Translate.exe" (
    echo ❌ ITM_Translate.exe not found in dist folder
    echo Please build the application first using build_release.py
    echo.
    pause
    exit /b 1
)

REM Create output directory
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo ✅ Inno Setup found
echo ✅ Application executable found
echo.

echo Building installer...
echo Command: %INNO_SETUP% "%SETUP_SCRIPT%"
echo.

REM Run Inno Setup compiler
%INNO_SETUP% "%SETUP_SCRIPT%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Installer built successfully!
    echo.
    echo Output location: %OUTPUT_DIR%
    echo.
    
    REM List generated files
    echo Generated files:
    for %%f in ("%OUTPUT_DIR%\*.exe") do (
        echo   📦 %%~nxf (%%~zf bytes)
    )
    
    echo.
    echo 🚀 Ready to distribute!
    
    REM Ask if user wants to open output folder
    set /p OPEN_FOLDER="Open output folder? (y/n): "
    if /i "%OPEN_FOLDER%"=="y" (
        start "" "%OUTPUT_DIR%"
    )
) else (
    echo.
    echo ❌ Installer build failed with error code %ERRORLEVEL%
    echo Please check the setup script and try again.
)

echo.
pause
