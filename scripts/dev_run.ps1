# QuickPaste Manager — 개발 실행
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Set-Location $Root

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "가상환경이 없습니다. bootstrap.ps1 을 먼저 실행하세요."
    exit 1
}

& ".\.venv\Scripts\python.exe" -m src.main
