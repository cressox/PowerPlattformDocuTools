<# 
.SYNOPSIS
    Startet den Power BI Documentation Generator.
.DESCRIPTION
    Wrapper-Skript für Windows PowerShell. Prüft Python-Installation,
    installiert ggf. Abhängigkeiten und startet das Tool.
.EXAMPLE
    .\run.ps1
#>

$ErrorActionPreference = "Stop"

# Check Python
$python = $null
foreach ($cmd in @("python3", "python", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            $python = $cmd
            Write-Host "✅ Gefunden: $ver" -ForegroundColor Green
            break
        }
    } catch { }
}

if (-not $python) {
    Write-Host "❌ Python 3 nicht gefunden. Bitte installieren: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

Push-Location $PSScriptRoot
try {
    # Install deps if needed
    $reqFile = Join-Path $PSScriptRoot "requirements.txt"
    if (Test-Path $reqFile) {
        Write-Host "📦 Prüfe Abhängigkeiten ..." -ForegroundColor Cyan

        $prevNativeErrPref = $PSNativeCommandUseErrorActionPreference
        $PSNativeCommandUseErrorActionPreference = $false
        & $python -m pip install -r $reqFile --disable-pip-version-check
        $installExitCode = $LASTEXITCODE
        $PSNativeCommandUseErrorActionPreference = $prevNativeErrPref

        if ($installExitCode -ne 0) {
            Write-Host "❌ Abhängigkeiten konnten nicht installiert werden (ExitCode: $installExitCode)." -ForegroundColor Red
            exit $installExitCode
        }
    }

    # Run
    Write-Host ""
    & $python -m src.main
}
finally {
    Pop-Location
}
