# QuickPaste Manager — 개발 환경 부트스트랩
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Set-Location $Root

if (-not (Test-Path ".venv")) {
    Write-Host "가상환경 생성 중..."
    python -m venv .venv
}

Write-Host "의존성 설치 중..."
& ".\.venv\Scripts\pip.exe" install -r requirements.txt

Write-Host "완료. 실행: .\scripts\dev_run.ps1"
