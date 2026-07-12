$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

Write-Host "Starting ATLAS by EWU..."

$pythonLauncher = Get-Command py -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue

if ($pythonLauncher) {
    Start-Process -FilePath "py" -ArgumentList @("-3.12", "-m", "uvicorn", "api.app:app", "--host", "127.0.0.1", "--port", "8000") -WorkingDirectory $PSScriptRoot
} elseif ($python) {
    Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "api.app:app", "--host", "127.0.0.1", "--port", "8000") -WorkingDirectory $PSScriptRoot
} else {
    Write-Host "Python was not found on this computer. Install Python 3.12, then run Start_ATLAS.bat again."
    Read-Host "Press Enter to close"
    exit 1
}

Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:8000"
Write-Host "ATLAS is starting at http://127.0.0.1:8000"
