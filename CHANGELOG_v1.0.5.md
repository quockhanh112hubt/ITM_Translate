# ITM Translate v1.0.5 - Release Notes

## 🔧 Bug Fixes
- **Fixed pywin32 import errors**: Resolved "pythoncom" and "win32com.client" import issues
  - Added `pywin32` to requirements.txt
  - Fixed startup shortcut creation functionality on Windows
  - Improved Windows integration capabilities

## ✨ Improvements
- **Enhanced Startup Functionality**: Windows startup shortcut creation now works properly
- **Better Dependency Management**: All required packages are now properly included
- **Improved Error Handling**: Better error messages for missing dependencies

## 🏗️ Technical Changes
- Added `pywin32` package to requirements
- Updated build process to include all necessary Windows components
- Improved compatibility with Windows COM interfaces

## 📋 Dependencies Updated
- Added: `pywin32` (for Windows COM interface support)
- Maintained all existing packages

## 🚀 Update Features
- Auto-update mechanism remains fully functional
- Seamless update process without hanging issues
- Safe file replacement during updates

---

### 📥 Installation
1. Download `ITM_Translate.exe`
2. Run the executable
3. Configure your hotkeys and settings
4. Enjoy seamless translation!

### 🔄 Updating from Previous Versions
- Use the built-in update checker: "Cập nhật chương trình" button in settings
- Or download and replace the executable manually

### 🐛 Bug Reports
If you encounter any issues, please report them on the GitHub repository.
