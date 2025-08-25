[Setup]
; Basic Information
AppName=ITM Translate
AppVersion=2.0.25
AppPublisher=ITM Semiconductor Vietnam Company Limited
AppPublisherURL=https://github.com/quockhanh112hubt/ITM_Translate
AppSupportURL=https://github.com/quockhanh112hubt/ITM_Translate/issues
AppUpdatesURL=https://github.com/quockhanh112hubt/ITM_Translate/releases
AppCopyright=Copyright © 2025 ITM Semiconductor Vietnam Company Limited
VersionInfoVersion=2.0.25.0
VersionInfoCompany=ITM Semiconductor Vietnam Company Limited
VersionInfoDescription=Professional AI Translation Tool
VersionInfoCopyright=Copyright © 2025 ITM Semiconductor Vietnam Company Limited
VersionInfoProductName=ITM Translate
VersionInfoProductVersion=2.0.25

; Installation Settings
DefaultDirName={localappdata}\ITM_Translate
DefaultGroupName=ITM Translate
PrivilegesRequired=lowest
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoAfterFile=README_INSTALL.txt
OutputDir=output
OutputBaseFilename=ITM_Translate_Setup_v2.0.25
SetupIconFile=..\Resource\icon.ico
UninstallDisplayIcon={app}\Resource\icon.ico
UninstallDisplayName=ITM Translate
Compression=lzma2/ultra64
SolidCompression=yes
DisableProgramGroupPage=no
DisableReadyPage=no
DisableWelcomePage=no

; Visual Settings
WizardStyle=modern
ShowLanguageDialog=auto
DisableDirPage=no

; System Requirements
MinVersion=6.1sp1
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Tasks (Checkboxes)
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startmenuicon"; Description: "Create Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "launchprogram"; Description: "Launch ITM Translate after installation"; GroupDescription: "After Installation"; Flags: checkedonce
Name: "visitwebsite"; Description: "Visit ITM Translate website"; GroupDescription: "After Installation"; Flags: unchecked

; Files to Install
[Files]
; Main executable
Source: "..\dist\ITM_Translate.exe"; DestDir: "{app}"; Flags: ignoreversion

; Resource files
Source: "..\Resource\*"; DestDir: "{app}\Resource"; Flags: ignoreversion recursesubdirs createallsubdirs

; Configuration files (but don't overwrite existing)
Source: "..\config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "..\version.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\startup.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "..\hotkeys.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

; Example files for user reference
Source: "..\api_keys.json.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

; Icons
[Icons]
; Start Menu icons
Name: "{group}\ITM Translate"; Filename: "{app}\ITM_Translate.exe"; IconFilename: "{app}\Resource\icon.ico"; Comment: "Professional AI Translation Tool"
Name: "{group}\{cm:UninstallProgram,ITM Translate}"; Filename: "{uninstallexe}"; IconFilename: "{app}\Resource\icon.ico"

; Desktop icon (optional)
Name: "{autodesktop}\ITM Translate"; Filename: "{app}\ITM_Translate.exe"; IconFilename: "{app}\Resource\icon.ico"; Comment: "Professional AI Translation Tool"; Tasks: desktopicon

; Quick Launch icon (optional, for older Windows)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\ITM Translate"; Filename: "{app}\ITM_Translate.exe"; IconFilename: "{app}\Resource\icon.ico"; Comment: "Professional AI Translation Tool"; Tasks: quicklaunchicon

; Registry entries
[Registry]
; Application settings (stored in user registry)
Root: HKCU; Subkey: "Software\ITM_Translate"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\ITM_Translate"; ValueType: string; ValueName: "Version"; ValueData: "2.0.25"; Flags: uninsdeletekey

; Run section (post-installation actions)
[Run]
; Launch program if requested
Filename: "{app}\ITM_Translate.exe"; Description: "{cm:LaunchProgram,ITM Translate}"; Flags: nowait postinstall skipifsilent; Tasks: launchprogram

; Visit website if requested
Filename: "https://github.com/quockhanh112hubt/ITM_Translate"; Description: "Visit ITM Translate website"; Flags: postinstall skipifsilent shellexec; Tasks: visitwebsite

; Uninstall section
[UninstallDelete]
; Clean up user data files (but preserve user config)
Type: files; Name: "{app}\translation_cache.json"
Type: files; Name: "{app}\translation_history.json"
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"

; Custom messages
[Messages]
BeveledLabel=ITM Translate v2.0.25 - Professional AI Translation Tool
SelectDirLabel3=Setup will install [name] into the following folder.%n%nNote: ITM Translate will be installed in your user directory to ensure proper file permissions for saving settings and translation data.

[CustomMessages]
LaunchProgram=Launch %1
CreateDesktopIcon=Create a &desktop icon
CreateQuickLaunchIcon=Create a &Quick Launch icon
AdditionalIcons=Additional icons:

; Code section for custom functionality
[Code]
var
  ProgressPage: TOutputProgressWizardPage;

procedure InitializeWizard;
begin
  // Create custom progress page
  ProgressPage := CreateOutputProgressPage('Installing ITM Translate', 
    'Please wait while Setup installs ITM Translate on your computer.');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  I: Integer;
  AppDataDir: String;
begin
  if CurStep = ssInstall then begin
    ProgressPage.Show;
    try
      for I := 0 to 100 do begin
        ProgressPage.SetProgress(I, 100);
        ProgressPage.SetText('Installing files... ' + IntToStr(I) + '%', '');
        Sleep(30); // Simulate installation time
      end;
    finally
      ProgressPage.Hide;
    end;
  end;
  
  // Post-installation: Set up user data directories
  if CurStep = ssPostInstall then begin
    AppDataDir := ExpandConstant('{app}');
    
    // Ensure the application directory has proper permissions for writing
    // This is automatically handled when installing to {localappdata}
    
    // Create user data subdirectories if they don't exist
    if not DirExists(AppDataDir + '\logs') then
      CreateDir(AppDataDir + '\logs');
    if not DirExists(AppDataDir + '\cache') then  
      CreateDir(AppDataDir + '\cache');
    if not DirExists(AppDataDir + '\backup') then
      CreateDir(AppDataDir + '\backup');
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Custom validation can be added here
  if CurPageID = wpSelectDir then begin
    // Validate installation directory
    if not DirExists(ExpandConstant('{app}')) then begin
      if not CreateDir(ExpandConstant('{app}')) then begin
        MsgBox('Cannot create installation directory. Please choose a different location.', 
               mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
end;
