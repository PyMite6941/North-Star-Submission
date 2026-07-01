<#
.SYNOPSIS
    North Star (Polaris) installer for Windows.
.DESCRIPTION
    Sets up the full offline stack: Python venv, the monorepo (editable install),
    Ollama, and the default models. Idempotent — safe to re-run.
.PARAMETER ChatModel
    Ollama chat model to pull (default: llama3.2).
.PARAMETER EmbedModel
    Ollama embedding model to pull (default: nomic-embed-text).
.PARAMETER SkipModels
    Skip pulling Ollama models (e.g. offline, or pull later).
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File install\install.ps1
.EXAMPLE
    .\install\install.ps1 -ChatModel qwen2.5:3b
#>
[CmdletBinding()]
param(
    [string]$ChatModel = "llama3.2",
    [string]$EmbedModel = "nomic-embed-text",
    [switch]$SkipModels
)

$ErrorActionPreference = "Stop"

# --- Move to repo root (this script lives in install/) -----------------------
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot
Write-Host "==> North Star installer (Windows)" -ForegroundColor Cyan
Write-Host "    Repo: $RepoRoot"

function Have($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

# --- 1. Python ---------------------------------------------------------------
$Python = $null
if (Have "py") { $Python = "py -3" }
elseif (Have "python") { $Python = "python" }

if (-not $Python) {
    Write-Host "==> Python not found. Attempting install via winget..." -ForegroundColor Yellow
    if (Have "winget") {
        winget install -e --id Python.Python.3.13 --accept-source-agreements --accept-package-agreements
        Write-Host "    Python installed. Re-open the terminal and re-run this script." -ForegroundColor Green
        exit 0
    }
    throw "Python 3.11+ is required. Install from https://www.python.org/downloads/ and re-run."
}

$ver = (& cmd /c "$Python --version") 2>&1
Write-Host "==> Using $ver"

# --- 2. Ollama ---------------------------------------------------------------
if (-not (Have "ollama")) {
    Write-Host "==> Ollama not found. Attempting install via winget..." -ForegroundColor Yellow
    if (Have "winget") {
        winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
    } else {
        Write-Host "    Install Ollama from https://ollama.com/download then re-run." -ForegroundColor Yellow
    }
}

# --- 3. Virtual environment + editable install -------------------------------
if (-not (Test-Path ".venv")) {
    Write-Host "==> Creating virtual environment (.venv)..."
    & cmd /c "$Python -m venv .venv"
}
$VenvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"

Write-Host "==> Installing the project (editable)..."
& $VenvPy -m pip install -U pip
& $VenvPy -m pip install -e .

# --- 4. .env -----------------------------------------------------------------
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "==> Created .env from .env.example"
}

# --- 5. Models ---------------------------------------------------------------
if (-not $SkipModels -and (Have "ollama")) {
    Write-Host "==> Pulling Ollama models (this can take a while)..." -ForegroundColor Cyan
    try {
        ollama pull $ChatModel
        ollama pull $EmbedModel
    } catch {
        Write-Host "    Could not pull models (is 'ollama serve' running?). Pull later with:" -ForegroundColor Yellow
        Write-Host "      ollama pull $ChatModel; ollama pull $EmbedModel"
    }
}

Write-Host ""
Write-Host "==> Done!" -ForegroundColor Green
Write-Host "    Activate:  .\.venv\Scripts\Activate.ps1"
Write-Host "    Verify:    polaris-study doctor"
Write-Host "    Try:       polaris-study ask `"make flashcards on the Krebs cycle`""
