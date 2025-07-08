# ITM Translate v1.0.6 - Release Notes

## 🔧 Major Bug Fixes
- **Fixed "Failed to load Python DLL" error**: Resolved critical DLL loading issues after updates
  - Enhanced PyInstaller spec file with complete hidden imports
  - Added proper pywin32 and COM interface dependencies
  - Improved executable startup reliability

## 🚀 Improved Update Mechanism
- **Enhanced Restart Process**: Better handling of application restart after updates
  - Added longer delay before file replacement
  - Improved batch script with better error handling
  - Added working directory context for reliable startup

## 🎯 User Experience Improvements
- **Better Update Dialog**: More informative restart options
  - Added 3-way choice: Auto restart / Manual restart / Cancel
  - Clear instructions for manual restart if needed
  - Better error messages with troubleshooting steps

## 🏗️ Technical Enhancements
- **Complete Dependencies**: All required packages properly included
  - Added: `pythoncom`, `win32com.client`, `pywintypes`
  - Added: `win32api`, `win32gui`, `win32con` 
  - Added: `pynput`, `google.generativeai`, `PIL`, `requests`
  - Enhanced PyInstaller build process

## 🧪 Testing & Reliability
- **Added Dependency Test Script**: `test_dependencies.py` for diagnostics
  - Tests all critical imports
  - Tests file access capabilities
  - Tests GUI creation
  - Provides troubleshooting information

## 📋 Dependencies Fixed
- ✅ `pywin32` - Windows COM interface
- ✅ `pythoncom` - Python COM support  
- ✅ `win32com.client` - COM client functionality
- ✅ `ttkbootstrap` - Modern UI themes
- ✅ `pynput` - Keyboard/mouse input
- ✅ `requests` - HTTP requests
- ✅ `PIL` - Image processing
- ✅ `google.generativeai` - AI translation

## 🔄 Update Process
This version specifically addresses the "Python DLL" error that occurred after updates. The update mechanism now:
1. Provides better restart options
2. Handles file replacement more reliably  
3. Includes proper error recovery
4. Offers manual restart as fallback

---

### 🚨 Important Notes for Users
If you still encounter "Failed to load Python DLL" errors:
1. **Try Manual Restart**: Choose "Manual restart" option in update dialog
2. **Delete .backup files**: Remove any .backup files in the application folder
3. **Restart Computer**: Sometimes a system restart helps clear DLL cache
4. **Clean Install**: Download fresh .exe if issues persist

### 📥 Installation
1. Download `ITM_Translate.exe`
2. Run the executable
3. Configure your settings
4. Use the built-in updater for future updates

### 🔄 Updating from Previous Versions
- **Recommended**: Use built-in update checker
- **Alternative**: Download and replace executable manually
- **If update fails**: Use manual restart option

### 🐛 Troubleshooting
- Run `test_dependencies.py` to diagnose issues
- Check GitHub issues for community solutions
- Report new problems with system information
