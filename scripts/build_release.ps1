# QuickPaste Manager — PyInstaller 릴리스 빌드 (Windows)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot "lib\python_env.ps1")

Set-Location $Root

$venvPython = Get-VenvPython -Root $Root
$venvPip = Get-VenvPip -Root $Root

if (-not (Test-Path $venvPython)) {
    Write-Host "가상환경이 없습니다. .\scripts\bootstrap.ps1 을 먼저 실행하세요." -ForegroundColor Red
    exit 1
}

Write-Host "PyInstaller 설치 확인..."
& $venvPip install pyinstaller --quiet

Write-Host "빌드 시작 (one-folder)..."
& $venvPython -m PyInstaller installer/quickpaste.spec --noconfirm --clean

$outDir = Join-Path $Root "dist\QuickPasteManager"
if (-not (Test-Path (Join-Path $outDir "QuickPasteManager.exe"))) {
    Write-Host "빌드 산출물을 찾을 수 없습니다: $outDir" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "빌드 완료: $outDir" -ForegroundColor Green
Write-Host "설치 패키지: Inno Setup이 설치되어 있으면"
Write-Host "  iscc installer\quickpaste.iss"
