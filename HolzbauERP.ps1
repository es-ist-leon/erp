# HolzbauERP Starter Script
Set-Location -Path $PSScriptRoot

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python gefunden: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python ist nicht installiert!" -ForegroundColor Red
    Write-Host "Bitte installieren Sie Python von https://www.python.org/"
    Read-Host "Druecken Sie Enter zum Beenden"
    exit 1
}

# Create venv if not exists
if (-not (Test-Path "venv")) {
    Write-Host "Erstelle virtuelle Python-Umgebung..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
& ".\venv\Scripts\Activate.ps1"

# Check dependencies
$pyqtInstalled = python -c "import PyQt6" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installiere Abhaengigkeiten..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
}

# Run application
Write-Host "Starte HolzbauERP..." -ForegroundColor Green
python -m app.main

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nFehler beim Starten der Anwendung." -ForegroundColor Red
    Read-Host "Druecken Sie Enter zum Beenden"
}
