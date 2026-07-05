param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

if ($Port -lt 1 -or $Port -gt 65535) {
    throw "Port must be between 1 and 65535."
}

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location -LiteralPath $RepoRoot

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "Creating local virtual environment..."
    python -m venv .venv
}

Write-Host "Installing wiki dependencies..."
& $VenvPython -m pip install -r requirements.txt

Write-Host "Starting NKU-AI-Study Wiki at http://127.0.0.1:$Port/"
Write-Host "Press Ctrl+C to stop."
& $VenvPython -m mkdocs serve -a "127.0.0.1:$Port"