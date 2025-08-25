# ITM Translate Installer Setup

This directory contains the installer configuration for ITM Translate.

## Files Structure:
- `setup.iss` - Main Inno Setup script
- `LICENSE.txt` - Software license agreement
- `README_INSTALL.txt` - Post-installation information
- `output/` - Generated installer files
- `WizardImage.bmp` - Left-side installer image (164x314 pixels)
- `WizardSmallImage.bmp` - Top-right installer image (55x55 pixels)

## Building the Installer:

### Prerequisites:
1. Install Inno Setup 6: https://jrsoftware.org/isinfo.php
2. Build the application first: `python build_release.py`

### Build Steps:
1. Run `build_installer.bat` from the project root
2. The installer will be generated in `installer/output/`

### Manual Build:
```bash
# Using Inno Setup command line
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
```

## Installer Features:
✅ License agreement with terms and conditions
✅ Custom installation directory (default: C:\Program Files\ITM_Translate)
✅ Desktop shortcut option
✅ Start Menu shortcut option
✅ Launch after installation option
✅ Visit website option
✅ Progress bar with percentage
✅ Professional appearance with custom icons
✅ Uninstaller included
✅ Registry cleanup

## Customization:
- Edit `setup.iss` to modify installer behavior
- Replace `LICENSE.txt` with updated terms
- Update `README_INSTALL.txt` for post-installation instructions
- Add custom images: WizardImage.bmp (164x314) and WizardSmallImage.bmp (55x55)

## Output:
- `ITM_Translate_Setup_v2.0.25.exe` - Main installer
- Automatic version detection from version.json
- Digitally signable (code signing certificate required)

Built with ❤️ by KhanhIT ITM Team
