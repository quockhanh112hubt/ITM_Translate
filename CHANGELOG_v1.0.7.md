# ITM Translate v1.0.7 - Release Notes

## 🔧 Major DLL Loading Fixes
- **Completely Rebuilt PyInstaller Configuration**: Enhanced spec file with comprehensive dependency collection
  - Added automatic collection of all `ttkbootstrap`, `win32com`, and `pythoncom` submodules
  - Disabled UPX compression to prevent DLL conflicts
  - Added runtime hooks for proper Windows COM initialization

## 🚀 Revolutionary Update Mechanism
- **New Safe Restart Approach**: Replaced batch scripts with Python-based updater
  - Uses dedicated Python script for file replacement
  - Proper file locking and error recovery
  - Graceful fallback to manual restart if auto-restart fails

## 🎯 Enhanced User Experience
- **Smart Restart Options**: Improved dialog with clear choices
  - **YES**: Auto-restart (experimental, safer approach)
  - **NO**: Manual restart with detailed step-by-step instructions
  - **CANCEL**: Continue with current version
  - Automatic folder opening for manual update process

## 🏗️ Technical Improvements
- **Complete Dependency Coverage**: All critical modules properly bundled
  - ✅ Full `win32com` ecosystem with all submodules
  - ✅ Complete `pythoncom` and `pywintypes` integration
  - ✅ Enhanced `ttkbootstrap` theme support
  - ✅ Comprehensive `PIL`, `requests`, and Google AI modules

## 📋 Build System Enhancements
- **Clean Build Process**: Using `--clean` flag to prevent cache issues
- **Enhanced Spec File**: Dynamic module collection prevents missing dependencies
- **Larger but Stable**: File size increased (~45MB) for better stability

## 🛠️ Manual Update Instructions
If auto-restart fails, the app now provides detailed manual instructions:

### Step-by-Step Manual Update:
1. **Exit Application**: Close all ITM Translate windows (Alt+F4)
2. **Open Program Folder**: Navigate to the folder containing ITM_Translate.exe
3. **Replace Files**:
   - Delete the old `ITM_Translate.exe`
   - Rename `ITM_Translate.exe.new` to `ITM_Translate.exe`
   - Delete any `.backup` files
4. **Launch**: Run the new `ITM_Translate.exe`

## 🚨 DLL Error Solutions
If you still encounter "Failed to load Python DLL":
1. **Restart Computer**: Clear system DLL cache
2. **Disable Antivirus**: Temporarily disable real-time protection
3. **Run as Administrator**: Right-click → "Run as administrator"
4. **Clean Install**: Download fresh executable from GitHub

## 🔄 What's Different This Version
- **Safer Updates**: Manual restart now recommended over auto-restart
- **Better Error Handling**: Clear instructions when auto-restart fails
- **Enhanced Compatibility**: More comprehensive Windows COM support
- **Improved Stability**: Better handling of Python runtime dependencies

---

### 📥 Installation & Update
1. **Fresh Install**: Download `ITM_Translate.exe` (47MB)
2. **From Previous Versions**: Use built-in updater, choose "Manual restart" if available
3. **If Update Fails**: Follow manual update instructions or download fresh

### 🔧 For Developers
- Enhanced `.spec` file with dynamic dependency collection
- Clean build process with `--clean` flag
- Comprehensive testing with `test_dependencies.py`

### 🐛 Troubleshooting
- **DLL Errors**: Follow manual restart instructions
- **Update Stuck**: Choose "Manual restart" option
- **Performance Issues**: Larger file size is normal for enhanced stability

### 💡 Recommendation
**For this update, we recommend choosing "Manual restart" option** instead of auto-restart to avoid any DLL loading issues. The manual process is now much clearer and includes automatic folder opening.
