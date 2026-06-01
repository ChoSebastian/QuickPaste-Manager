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

$appVersion = (& $venvPython -c "from src.version import APP_VERSION; print(APP_VERSION)").Trim()
Write-Host "QuickPaste Manager v$appVersion — PyInstaller 빌드" -ForegroundColor Cyan

# 이전 산출물·로컬 데이터 미러 제거 (사용자 DB가 패키지에 섞이지 않도록)
$distRoot = Join-Path $Root "dist"
$buildDir = Join-Path $Root "build"
$localMirror = Join-Path $Root "QuickPasteManager"

foreach ($path in @($distRoot, $buildDir, $localMirror)) {
    if (Test-Path $path) {
        Write-Host "정리: $path"
        Remove-Item $path -Recurse -Force
    }
}

Write-Host "PyInstaller 설치 확인..."
& $venvPip install pyinstaller --quiet

Write-Host "빌드 시작 (one-folder, 데이터 미포함)..."
& $venvPython -m PyInstaller installer/quickpaste.spec --noconfirm --clean

$outDir = Join-Path $Root "dist\QuickPasteManager"
$exePath = Join-Path $outDir "QuickPasteManager.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "빌드 산출물을 찾을 수 없습니다: $outDir" -ForegroundColor Red
    exit 1
}

# 사용자 데이터 파일이 번들에 포함되지 않았는지 검사
$forbidden = Get-ChildItem $outDir -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -in ".db", ".sqlite" -or $_.Name -eq "settings.json" }
if ($forbidden) {
    Write-Host "빌드 산출물에 사용자 데이터가 포함되어 있습니다:" -ForegroundColor Red
    $forbidden | ForEach-Object { Write-Host "  $($_.FullName)" }
    exit 1
}

Write-Host ""
Write-Host "빌드 완료: $outDir" -ForegroundColor Green
Write-Host "버전: v$appVersion"
Write-Host "설치 패키지: .\installer\build_installer.ps1 (Inno Setup)"
