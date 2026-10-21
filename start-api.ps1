$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot 'backend')

if (-not (Test-Path '.venv')) { py -m venv .venv }
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

if (-not $env:DATABASE_URL) { $env:DATABASE_URL = 'sqlite:///./finsight_dev.db' }
if (-not $env:JWT_SECRET_KEY) { $env:JWT_SECRET_KEY = 'replace-this-with-a-long-random-secret-before-use' }
if (-not $env:ALLOW_DEV_SECRET) { $env:ALLOW_DEV_SECRET = '1' }
if (-not $env:OPENROUTER_MODEL) { $env:OPENROUTER_MODEL = 'openrouter/free' }

if (-not $env:OPENROUTER_API_KEY -and -not $env:ANTHROPIC_API_KEY) {
    Write-Host ''
    Write-Host 'FinSight free AI setup (OpenRouter)' -ForegroundColor Cyan
    Write-Host 'Get a key at https://openrouter.ai/keys and choose a free model.'
    Write-Host 'Paste your OpenRouter key below. Input is hidden and kept only in this terminal session.'
    Write-Host 'Press Enter to continue without live AI (rules-based fallback will be used).'
    $secureKey = Read-Host 'OPENROUTER_API_KEY' -AsSecureString
    if ($secureKey.Length -gt 0) {
        $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
        try { $env:OPENROUTER_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
        finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    }
}

if ($env:OPENROUTER_API_KEY) {
    Write-Host "OpenRouter AI configured (model: $env:OPENROUTER_MODEL). Key will not be written to a file." -ForegroundColor Green
} elseif ($env:ANTHROPIC_API_KEY) {
    Write-Host "Anthropic AI configured (model: $env:ANTHROPIC_MODEL). Key will not be written to a file." -ForegroundColor Green
} else {
    Write-Host 'No API key supplied. FinSight will use the clearly labelled rules-based fallback.' -ForegroundColor Yellow
}
Write-Host 'Starting FinSight API at http://127.0.0.1:8000' -ForegroundColor Cyan
uvicorn app.main:app --reload
