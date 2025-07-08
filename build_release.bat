@echo off
echo ========================================
echo  ITM Translate - Auto Build & Release
echo ========================================

:: Kiểm tra Git repository
if not exist ".git" (
    echo ERROR: Đây không phải là Git repository!
    pause
    exit /b 1
)

:: Kiểm tra thay đổi chưa commit
git status --porcelain > temp_status.txt
set /p HAS_CHANGES=<temp_status.txt
del temp_status.txt

if not "%HAS_CHANGES%"=="" (
    echo WARNING: Có thay đổi chưa được commit!
    echo Bạn có muốn tiếp tục? (y/N)
    set /p CONTINUE=
    if not "%CONTINUE%"=="y" if not "%CONTINUE%"=="Y" (
        echo Đã hủy.
        pause
        exit /b 1
    )
)

:: Lấy version hiện tại
set /p NEW_VERSION=<nul
for /f "tokens=2 delims=:" %%a in ('findstr "version" version.json') do (
    set VERSION_LINE=%%a
)
for /f "tokens=1 delims=," %%a in ("%VERSION_LINE%") do (
    set NEW_VERSION=%%a
)
set NEW_VERSION=%NEW_VERSION:"=%
set NEW_VERSION=%NEW_VERSION: =%

echo Version hiện tại: %NEW_VERSION%
echo.

:: Nhập version mới
echo Nhập version mới (Enter để giữ nguyên):
set /p INPUT_VERSION=
if not "%INPUT_VERSION%"=="" (
    set NEW_VERSION=%INPUT_VERSION%
)

:: Tạo build number dựa trên timestamp
for /f %%a in ('wmic os get localdatetime ^| find "."') do set datetime=%%a
set BUILD_NUM=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%%datetime:~8,2%

echo.
echo Version: %NEW_VERSION%
echo Build: %BUILD_NUM%
echo.

:: Cập nhật version.json
echo Cập nhật version.json...
(
echo {
echo     "version": "%NEW_VERSION%",
echo     "build": "%BUILD_NUM%",
echo     "release_date": "%date%",
echo     "description": "Auto build release"
echo }
) > version.json

:: Build với PyInstaller
echo.
echo ========================================
echo  Bắt đầu build executable...
echo ========================================

if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

:: Build với PyInstaller (ưu tiên spec file nếu có)
if exist "ITM_Translate.spec" (
    echo Sử dụng spec file để build...
    python -m PyInstaller ITM_Translate.spec
) else (
    echo Sử dụng command line để build...
    python -m PyInstaller --onefile --windowed --hidden-import=ttkbootstrap --icon="Resource/icon.ico" --add-data "Resource/icon.ico;Resource" --name="ITM_Translate" ITM_Translate.py
)

if not exist "dist\ITM_Translate.exe" (
    echo ERROR: Build thất bại!
    pause
    exit /b 1
)

echo Build thành công: dist\ITM_Translate.exe

:: Commit và tạo tag
echo.
echo ========================================
echo  Git commit và tạo tag...
echo ========================================

git add .
git commit -m "Release v%NEW_VERSION% - Build %BUILD_NUM%"
git tag -a "v%NEW_VERSION%" -m "Release version %NEW_VERSION%"

echo Đã tạo tag: v%NEW_VERSION%

:: Hỏi có muốn push không
echo.
echo Bạn có muốn push lên GitHub không? (y/N)
set /p PUSH_CONFIRM=
if "%PUSH_CONFIRM%"=="y" (
    echo Đang push...
    git push origin main
    git push origin --tags
    echo Push thành công!
) else (
    echo Đã skip push. Bạn có thể push sau bằng:
    echo   git push origin main
    echo   git push origin --tags
)

echo.
echo ========================================
echo  Hoàn thành!
echo ========================================
echo File build: dist\ITM_Translate.exe
echo Version: %NEW_VERSION%
echo Build: %BUILD_NUM%
echo Tag: v%NEW_VERSION%
echo.
echo Tiếp theo:
echo 1. Tạo release trên GitHub từ tag v%NEW_VERSION%
echo 2. Upload file dist\ITM_Translate.exe vào release
echo 3. Viết changelog cho release
echo.
pause
