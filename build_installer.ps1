# ITM Translate Installer Builder
# PowerShell version with auto Inno Setup download

param(
    [switch]$AutoDownload = $false
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   ITM Translate - Installer Builder" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan

# Configuration
$InnoSetupUrl = "https://files.jrsoftware.org/is/6/innosetup-6.2.2.exe"
$InnoSetupInstaller = "$env:TEMP\innosetup-6.2.2.exe"
$InnoSetupPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
$ProjectDir = $PSScriptRoot
$SetupScript = Join-Path $ProjectDir "installer\setup.iss"
$OutputDir = Join-Path $ProjectDir "installer\output"
$ExePath = Join-Path $ProjectDir "dist\ITM_Translate.exe"

Write-Host ""
Write-Host "Checking requirements..." -ForegroundColor Yellow

# Check if application is built
if (-not (Test-Path $ExePath)) {
    Write-Host "[Error] ITM_Translate.exe not found in dist folder" -ForegroundColor Red
    Write-Host "Please build the application first using build_release.py" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Inno Setup is installed
if (-not (Test-Path $InnoSetupPath)) {
    Write-Host "[Error] Inno Setup not found at $InnoSetupPath" -ForegroundColor Red
    
    if ($AutoDownload -or (Read-Host "Download and install Inno Setup automatically? (y/n)") -eq 'y') {
        Write-Host ""
        Write-Host "Downloading Inno Setup..." -ForegroundColor Yellow
        
        try {
            # Download Inno Setup
            Invoke-WebRequest -Uri $InnoSetupUrl -OutFile $InnoSetupInstaller -UseBasicParsing
            Write-Host "[Success] Download completed" -ForegroundColor Green
            
            # Install Inno Setup
            Write-Host "Installing Inno Setup (requires administrator privileges)..." -ForegroundColor Yellow
            Start-Process -FilePath $InnoSetupInstaller -ArgumentList "/VERYSILENT /NORESTART" -Wait -Verb RunAs
            
            # Clean up
            Remove-Item $InnoSetupInstaller -ErrorAction SilentlyContinue
            
            # Check if installation was successful
            if (Test-Path $InnoSetupPath) {
                Write-Host "[Success] Inno Setup installed successfully" -ForegroundColor Green
            } else {
                Write-Host "[Error] Inno Setup installation failed" -ForegroundColor Red
                exit 1
            }
        }
        catch {
            Write-Host "[Error] Failed to download/install Inno Setup: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "Please download manually from: https://jrsoftware.org/isinfo.php" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "Please install Inno Setup 6 from: https://jrsoftware.org/isinfo.php" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "[Success] Inno Setup found" -ForegroundColor Green
Write-Host "[Success] Application executable found" -ForegroundColor Green
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

Write-Host "Building installer..." -ForegroundColor Yellow
Write-Host "Command: `"$InnoSetupPath`" `"$SetupScript`"" -ForegroundColor Gray
Write-Host ""

# Run Inno Setup compiler
try {
    # Change to installer directory for relative paths to work
    Push-Location (Join-Path $ProjectDir "installer")
    $process = Start-Process -FilePath $InnoSetupPath -ArgumentList "`"setup.iss`"" -Wait -PassThru -NoNewWindow
    Pop-Location
    
    if ($process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "[Success] Installer built successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Output location: $OutputDir" -ForegroundColor Cyan
        Write-Host ""
        
        # List generated files
        Write-Host "Generated files:" -ForegroundColor Yellow
        Get-ChildItem -Path $OutputDir -Filter "*.exe" | ForEach-Object {
            $sizeInMB = [math]::Round($_.Length / 1MB, 2)
            Write-Host "  [Package] $($_.Name) ($sizeInMB MB)" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "[Success] Ready to distribute!" -ForegroundColor Green
        
        # Ask if user wants to open output folder
        $openFolder = Read-Host "Open output folder? (y/n)"
        if ($openFolder -eq 'y') {
            Start-Process -FilePath "explorer.exe" -ArgumentList $OutputDir
        }
    } else {
        Write-Host ""
        Write-Host "[Error] Installer build failed with exit code $($process.ExitCode)" -ForegroundColor Red
        Write-Host "Please check the setup script and try again." -ForegroundColor Yellow
    }
}
catch {
    Write-Host ""
    Write-Host "[Error] Error running Inno Setup: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
