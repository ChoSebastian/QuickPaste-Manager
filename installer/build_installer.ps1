# QuickPaste Manager — PyInstaller + Inno Setup 설치 패키지
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
. (Join-Path $Root "scripts\lib\find_iscc.ps1")

& (Join-Path $Root "scripts\build_release.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$iscc = Get-InnoSetupCompiler
if (-not $iscc) {
    Write-Host "Inno Setup을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "설치: winget install JRSoftware.InnoSetup" -ForegroundColor Yellow
    exit 1
}

Write-Host "Inno Setup: $iscc"
Write-Host "설치 패키지 빌드 중..."
& $iscc (Join-Path $Root "installer\quickpaste.iss")
if ($LASTEXITCODE -ne 0) {
    Write-Host "Inno Setup 빌드 실패 (exit $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

$setup = Get-ChildItem (Join-Path $Root "dist") -Filter "QuickPasteManager-Setup-*.exe" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($setup) {
    Write-Host ""
    Write-Host "설치 파일 생성 완료:" -ForegroundColor Green
    Write-Host "  $($setup.FullName)"
    Write-Host "  크기: $([math]::Round($setup.Length / 1MB, 2)) MB"
} else {
    Write-Host "설치 exe를 dist에서 찾지 못했습니다." -ForegroundColor Yellow
    exit 1
}
