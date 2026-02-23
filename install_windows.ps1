# Windows PowerShell installation script for Thermalright LCD Control
# Run this script as Administrator in PowerShell

Write-Host "=========================================="
Write-Host "Thermalright LCD Control - Windows Installer"
Write-Host "=========================================="
Write-Host ""

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click on PowerShell and select 'Run as administrator', then run this script again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8 or higher from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    $pipVersion = python -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "pip not found"
    }
    Write-Host "pip detected: $pipVersion" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "ERROR: pip is not available" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please reinstall Python and make sure pip is included" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment if it doesn't exist
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvDir = Join-Path $scriptDir "venv"

if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Write-Host ""
        Write-Host "The Python venv module appears to be missing or incomplete." -ForegroundColor Yellow
        Write-Host "Please reinstall Python with all standard library modules included." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Virtual environment created successfully." -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
    Write-Host ""
}

# Set pip path to use the venv
$venvPip = Join-Path $venvDir "Scripts\pip.exe"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

# Function to search for an application in Program Files
function Find-Application {
    param(
        [string]$AppName,
        [string[]]$ExecutableNames,
        [string[]]$CommonSubdirs,
        [switch]$SearchAllDrives
    )
    
    # Get Program Files directories
    $programFilesDirs = @()
    if ($env:ProgramFiles) { $programFilesDirs += $env:ProgramFiles }
    if ($env:ProgramW6432) { $programFilesDirs += $env:ProgramW6432 }
    if (${env:ProgramFiles(x86)}) { $programFilesDirs += ${env:ProgramFiles(x86)} }
    
    # Remove duplicates and non-existent paths
    $programFilesDirs = $programFilesDirs | Select-Object -Unique | Where-Object { Test-Path $_ }
    
    # First check common subdirectories in Program Files
    foreach ($baseDir in $programFilesDirs) {
        foreach ($subdir in $CommonSubdirs) {
            $searchPath = Join-Path $baseDir $subdir
            if (Test-Path $searchPath) {
                foreach ($exeName in $ExecutableNames) {
                    $exePath = Join-Path $searchPath $exeName
                    if (Test-Path $exePath) {
                        return $exePath
                    }
                }
            }
        }
    }
    
    # If not found and SearchAllDrives is enabled, search other drives
    if ($SearchAllDrives) {
        Write-Host "  Searching additional drives for $AppName..." -ForegroundColor Gray
        
        # Get all fixed drives
        $drives = Get-PSDrive -PSProvider FileSystem | Where-Object { 
            $_.Root -match '^[A-Z]:\\$' -and (Test-Path $_.Root)
        }
        
        foreach ($drive in $drives) {
            # Skip C: drive as it's already searched
            if ($drive.Name -eq 'C') { continue }
            
            # Check common installation directories on other drives
            $drivePaths = @(
                "$($drive.Root)Program Files",
                "$($drive.Root)Program Files (x86)",
                "$($drive.Root)Games",
                "$($drive.Root)"
            )
            
            foreach ($basePath in $drivePaths) {
                if (-not (Test-Path $basePath)) { continue }
                
                foreach ($subdir in $CommonSubdirs) {
                    $searchPath = Join-Path $basePath $subdir
                    if (Test-Path $searchPath) {
                        foreach ($exeName in $ExecutableNames) {
                            $exePath = Join-Path $searchPath $exeName
                            if (Test-Path $exePath) {
                                Write-Host "  Found on drive $($drive.Name):\" -ForegroundColor Cyan
                                return $exePath
                            }
                        }
                    }
                }
            }
        }
    }
    
    # If still not found, do a more thorough search in Program Files (limited depth)
    foreach ($baseDir in $programFilesDirs) {
        foreach ($exeName in $ExecutableNames) {
            $found = Get-ChildItem -Path $baseDir -Filter $exeName -Recurse -ErrorAction SilentlyContinue -Depth 3 | Select-Object -First 1
            if ($found) {
                return $found.FullName
            }
        }
    }
    
    return $null
}

# Detect iStripper
Write-Host "Searching for installed applications..." -ForegroundColor Cyan
Write-Host ""

# Ask user if they want to search additional drives
Write-Host "Do you want to search all drives for iStripper? (Y/N)" -ForegroundColor Cyan
Write-Host "  (This may take longer but finds installations on any drive)" -ForegroundColor Gray
$searchAllDrives = Read-Host
$shouldSearchAllDrives = ($searchAllDrives -eq "Y" -or $searchAllDrives -eq "y")
Write-Host ""

$iStripperPath = Find-Application -AppName "iStripper" `
    -ExecutableNames @("iStripper.exe", "vghd.exe") `
    -CommonSubdirs @("iStripper", "Totem Entertainment", "VirtuaGirl HD") `
    -SearchAllDrives:$shouldSearchAllDrives

if ($iStripperPath) {
    Write-Host "✓ iStripper detected: $iStripperPath" -ForegroundColor Green
} else {
    Write-Host "○ iStripper not found (optional)" -ForegroundColor Yellow
    if (-not $shouldSearchAllDrives) {
        Write-Host "  Tip: Run installer again and choose 'Y' to search all drives" -ForegroundColor Gray
    }
}

# Detect VLC
$vlcPath = Find-Application -AppName "VLC" `
    -ExecutableNames @("vlc.exe") `
    -CommonSubdirs @("VLC", "VideoLAN\VLC")

if ($vlcPath) {
    Write-Host "✓ VLC Media Player detected: $vlcPath" -ForegroundColor Green
} else {
    Write-Host "○ VLC Media Player not found (optional)" -ForegroundColor Yellow
}

Write-Host ""

# Install dependencies using the virtual environment
Write-Host "Installing thermalright-lcd-control package and dependencies..." -ForegroundColor Cyan
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

# Upgrade pip in venv first
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Failed to upgrade pip, continuing with current version..." -ForegroundColor Yellow
}

# Install the package with Windows-specific extras from pyproject.toml
Push-Location $scriptDir
& $venvPip install -e ".[windows]"
$installResult = $LASTEXITCODE
Pop-Location
if ($installResult -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to install package dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[OK] Package installed successfully" -ForegroundColor Green

# -------------------------------------------------------
# Install hidapi.dll (native HID library for Windows)
# -------------------------------------------------------
function Install-HidapiDll {
    param([string]$TargetVenvDir)

    $dllDest = Join-Path $TargetVenvDir "Scripts\hidapi.dll"
    if (Test-Path $dllDest) {
        Write-Host "[OK] hidapi.dll already present in $TargetVenvDir\Scripts\" -ForegroundColor Green
        return
    }

    Write-Host "Downloading hidapi native library for Windows HID device support..." -ForegroundColor Cyan
    $zipPath    = Join-Path $env:TEMP "hidapi-win.zip"
    $extractDir = Join-Path $env:TEMP "hidapi-win"

    try {
        Invoke-WebRequest -Uri "https://github.com/libusb/hidapi/releases/download/hidapi-0.14.0/hidapi-win.zip" `
            -OutFile $zipPath -UseBasicParsing -TimeoutSec 30
        Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force

        # The archive may place the DLL at x64\hidapi.dll or hidapi-win\x64\hidapi.dll
        $dllSrc = Join-Path $extractDir "x64\hidapi.dll"
        if (-not (Test-Path $dllSrc)) {
            $dllSrc = Get-ChildItem -Path $extractDir -Recurse -Filter "hidapi.dll" |
                      Where-Object { $_.DirectoryName -match "x64" } |
                      Select-Object -First 1 -ExpandProperty FullName
        }

        if ($dllSrc -and (Test-Path $dllSrc)) {
            Copy-Item $dllSrc -Destination $dllDest -Force
            Write-Host "[OK] hidapi.dll installed to $TargetVenvDir\Scripts\" -ForegroundColor Green
        } else {
            Write-Host "[!!] hidapi.dll not found in downloaded archive." -ForegroundColor Yellow
            Write-Host "     Please install manually: https://github.com/libusb/hidapi/releases" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[!!] Warning: Could not download hidapi.dll automatically: $_" -ForegroundColor Yellow
        Write-Host "     HID devices (0x0418:0x5304, 0x0416:0x5302) require hidapi.dll" -ForegroundColor Yellow
        Write-Host "     Place hidapi.dll in: $TargetVenvDir\Scripts\" -ForegroundColor Yellow
        Write-Host "     Manual download: https://github.com/libusb/hidapi/releases" -ForegroundColor Yellow
    } finally {
        if (Test-Path $zipPath)    { Remove-Item $zipPath    -Force -ErrorAction SilentlyContinue }
        if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue }
    }
}

Install-HidapiDll -TargetVenvDir $venvDir

# -------------------------------------------------------
# Detect and install into IS venv (E:\IS) if present
# -------------------------------------------------------
$isVenvPath = $null
foreach ($drive in @('E','D','C','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')) {
    $candidate = "${drive}:\IS"
    if (Test-Path (Join-Path $candidate "Scripts\python.exe")) {
        $isVenvPath = $candidate
        break
    }
}

if ($isVenvPath) {
    Write-Host ""
    Write-Host "Found IS virtual environment at $isVenvPath" -ForegroundColor Cyan
    Write-Host "Installing thermalright-lcd-control into IS venv..." -ForegroundColor Cyan

    $isVenvPip = Join-Path $isVenvPath "Scripts\pip.exe"
    Push-Location $scriptDir
    & $isVenvPip install --upgrade pip 2>&1 | Out-Null
    & $isVenvPip install -e ".[windows]"
    Pop-Location
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Package installed into IS venv" -ForegroundColor Green
    } else {
        Write-Host "[!!] Warning: Could not install package into IS venv" -ForegroundColor Yellow
    }

    Install-HidapiDll -TargetVenvDir $isVenvPath
}

# Create configuration file with detected applications
$configDir = Join-Path $env:LOCALAPPDATA "thermalright-lcd-control"
$configFile = Join-Path $configDir "detected_apps.json"

if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$detectedApps = @{
    "istripper_path" = $iStripperPath
    "vlc_path" = $vlcPath
    "detection_date" = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
}

$detectedApps | ConvertTo-Json | Set-Content -Path $configFile

Write-Host "Configuration saved to: $configFile" -ForegroundColor Cyan
Write-Host ""

Write-Host "=========================================="
Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "=========================================="
Write-Host ""

# Show detected applications summary
if ($iStripperPath -or $vlcPath) {
    Write-Host "Detected Applications:" -ForegroundColor Cyan
    if ($iStripperPath) {
        Write-Host "  • iStripper: $iStripperPath" -ForegroundColor Green
        Write-Host "    You can capture iStripper content using window capture mode" -ForegroundColor Gray
    }
    if ($vlcPath) {
        Write-Host "  • VLC: $vlcPath" -ForegroundColor Green
        Write-Host "    You can capture VLC player content using window capture mode" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "  run_gui_windows.bat (double-click to launch)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or run manually with the virtual environment:" -ForegroundColor Cyan
Write-Host "  1. Activate: $venvDir\Scripts\activate.bat" -ForegroundColor Yellow
Write-Host "  2. Run:      python -m thermalright_lcd_control.main_gui" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: Video playback is enabled without audio by default" -ForegroundColor Green
Write-Host "Supported video formats: MP4, AVI, MKV, MOV, WEBM, FLV, WMV, M4V" -ForegroundColor Green
Write-Host ""

# Offer to create a desktop shortcut
Write-Host "Would you like to create a desktop shortcut? (Y/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktopPath "Thermalright LCD Control.lnk"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $venvPython
    $Shortcut.Arguments = "-m thermalright_lcd_control.main_gui"
    $Shortcut.WorkingDirectory = $scriptDir
    $Shortcut.Description = "Thermalright LCD Control"
    $Shortcut.Save()
    
    Write-Host ""
    Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
}

Read-Host "Press Enter to exit"
