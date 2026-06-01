# QuickPaste Manager — 개발 실행
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot "lib\python_env.ps1")

Set-Location $Root

$venvPython = Get-VenvPython -Root $Root

if (-not (Test-Path $venvPython)) {
    Write-Host "가상환경이 없습니다. bootstrap.ps1 을 먼저 실행하세요." -ForegroundColor Yellow
    Write-Host "  .\scripts\bootstrap.ps1"
    exit 1
}

& $venvPython -m src.main
