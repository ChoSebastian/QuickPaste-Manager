# QuickPaste Manager — 개발 환경 부트스트랩
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot "lib\python_env.ps1")

Set-Location $Root

$python = Ensure-Python
Write-Host "Python: $python"

$venvPython = Get-VenvPython -Root $Root
$venvPip = Get-VenvPip -Root $Root

if (-not (Test-Path $venvPython)) {
    Write-Host "가상환경 생성 중..."
    & $python -m venv .venv
    if (-not (Test-Path $venvPython)) {
        Write-Host "가상환경 생성에 실패했습니다." -ForegroundColor Red
        exit 1
    }
}

Write-Host "의존성 설치 중..."
& $venvPip install -r requirements.txt

Write-Host "완료. 실행: .\scripts\dev_run.ps1"
