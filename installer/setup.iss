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
Root: HKCU; Subkey: "Software\ITM_Translate"; ValueType: string; ValueName: "UninstallString"; ValueData: "{uninstallexe}"; Flags: uninsdeletekey

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
const
  WM_CLOSE = $0010;

var
  ProgressPage: TOutputProgressWizardPage;
  MaintenancePage: TInputOptionWizardPage;

// Function to check if ITM Translate is running
function IsAppRunning(): Boolean;
var
  ResultCode: Integer;
  TempFile: String;
  Lines: TArrayOfString;
  I: Integer;
begin
  Result := False;
  try
    TempFile := ExpandConstant('{tmp}\processes.txt');
    
    // Run tasklist and save output to temp file
    if Exec('cmd', '/c tasklist /FI "IMAGENAME eq ITM_Translate.exe" > "' + TempFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then begin
      // Read the temp file and check if ITM_Translate.exe is listed
      if LoadStringsFromFile(TempFile, Lines) then begin
        for I := 0 to GetArrayLength(Lines) - 1 do begin
          if Pos('ITM_Translate.exe', Lines[I]) > 0 then begin
            Result := True;
            Break;
          end;
        end;
      end;
      DeleteFile(TempFile);
    end;
  except
    Result := False;
  end;
end;

// Function to check if ITM Translate is already installed
function IsAppInstalled(): Boolean;
var
  InstallPath: String;
begin
  Result := False;
  // Check registry for existing installation
  if RegQueryStringValue(HKCU, 'Software\ITM_Translate', 'InstallPath', InstallPath) then begin
    if (InstallPath <> '') and DirExists(InstallPath) and FileExists(InstallPath + '\ITM_Translate.exe') then begin
      Result := True;
    end else begin
      // If registry exists but files don't exist, clean up registry
      RegDeleteKeyIncludingSubkeys(HKCU, 'Software\ITM_Translate');
      Result := False;
    end;
  end;
end;

procedure InitializeWizard;
var
  IsInstalled: Boolean;
begin
  // Create custom progress page
  ProgressPage := CreateOutputProgressPage('Installing ITM Translate', 
    'Please wait while Setup installs ITM Translate on your computer.');
    
  // Check if app is installed (this will also clean up invalid registry entries)
  IsInstalled := IsAppInstalled();
    
  // Create maintenance page for existing installations
  if IsInstalled then begin
    MaintenancePage := CreateInputOptionPage(wpWelcome,
      'ITM Translate Setup', 'ITM Translate is already installed on this computer.',
      'Please select how you would like to proceed:', True, False);
    MaintenancePage.Add('&Repair ITM Translate');
    MaintenancePage.Add('&Uninstall ITM Translate');
    MaintenancePage.Add('&Update ITM Translate (recommended)');
    MaintenancePage.Values[2] := True; // Default to Update
  end else begin
    MaintenancePage := nil; // Ensure it's nil for new installations
  end;
end;

function InitializeSetup(): Boolean;
var
  Response: Integer;
  ResultCode: Integer;
begin
  Result := True;
  
  // Only check for running process if it's actually running
  if IsAppRunning() then begin
    // Process found - ask user what to do
    Response := MsgBox('ITM Translate is currently running.' + #13#10 + 
                      'Setup needs to close the application to continue installation.' + #13#10 + #13#10 +
                      'Click OK to close ITM Translate and continue, or Cancel to exit Setup.',
                      mbConfirmation, MB_OKCANCEL);
    
    if Response = IDOK then begin
      // Only terminate if user agrees
      if not Exec('taskkill', '/F /IM ITM_Translate.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then begin
        MsgBox('Failed to close ITM Translate. Please close the application manually and run Setup again.',
               mbError, MB_OK);
        Result := False;
        Exit;
      end;
      Sleep(2000); // Wait for process to fully terminate
    end else begin
      // User cancelled - exit setup WITHOUT terminating process
      Result := False;
      Exit;
    end;
  end;
  // If no process is running, continue normally
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

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  
  // For new installations, only skip maintenance page
  if (MaintenancePage = nil) then begin
    // This is a new installation - show all normal pages (Welcome, License, etc.)
    Result := False;
  end else begin
    // This is maintenance mode - skip maintenance page for new installs shouldn't happen
    if (PageID = MaintenancePage.ID) and not IsAppInstalled() then begin
      Result := True;
    end;
    
    // If user chose uninstall, skip normal installation pages
    if Assigned(MaintenancePage) and (MaintenancePage.Values[1] = True) then begin
      if (PageID = wpSelectDir) or (PageID = wpSelectComponents) or 
         (PageID = wpSelectProgramGroup) or (PageID = wpSelectTasks) then begin
        Result := True;
      end;
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  UninstallString: String;
  ResultCode: Integer;
begin
  Result := True;
  
  // Handle maintenance page selection
  if Assigned(MaintenancePage) and (CurPageID = MaintenancePage.ID) then begin
    if MaintenancePage.Values[1] = True then begin
      // Uninstall selected
      if RegQueryStringValue(HKCU, 'Software\ITM_Translate', 'UninstallString', UninstallString) then begin
        if MsgBox('This will uninstall ITM Translate from your computer. Continue?', 
                  mbConfirmation, MB_YESNO) = IDYES then begin
          Exec(UninstallString, '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
          MsgBox('ITM Translate has been uninstalled successfully.', mbInformation, MB_OK);
          // Exit setup completely after uninstall
          PostMessage(WizardForm.Handle, WM_CLOSE, 0, 0);
        end;
      end else begin
        MsgBox('Uninstall information not found. Please use Windows Add/Remove Programs.', 
               mbError, MB_OK);
      end;
      Result := False; // Don't continue to next page
      Exit;
    end;
    
    if MaintenancePage.Values[0] = True then begin
      // Repair selected - continue with normal installation
      MsgBox('Setup will now repair your ITM Translate installation.', 
             mbInformation, MB_OK);
    end;
    
    if MaintenancePage.Values[2] = True then begin
      // Update selected - continue with normal installation
      MsgBox('Setup will now update ITM Translate to the latest version.', 
             mbInformation, MB_OK);
    end;
  end;
  
  // Custom validation for directory selection
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
