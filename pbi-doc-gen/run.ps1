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
            Write-Host "[OK] Python gefunden: $ver" -ForegroundColor Green
            break
        }
    } catch { }
}

if (-not $python) {
    Write-Host "[ERROR] Python 3 nicht gefunden. Bitte installieren: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Install deps if neededs
$reqFile = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $reqFile) {
    Write-Host "[INFO] Pruefe Abhaengigkeiten ..." -ForegroundColor Cyan
    $pipOutput = & $python -m pip install -r $reqFile --disable-pip-version-check 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Installation der Abhaengigkeiten fehlgeschlagen." -ForegroundColor Red
        if ($pipOutput) {
            $pipOutput | ForEach-Object { Write-Host $_ }
        }
        exit $LASTEXITCODE
    }
}

# Run
Write-Host ""
& $python -m src.main
