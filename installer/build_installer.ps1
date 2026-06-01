# QuickPaste Manager — PyInstaller + Inno Setup 설치 패키지
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
. (Join-Path $Root "scripts\lib\find_iscc.ps1")
. (Join-Path $Root "scripts\lib\python_env.ps1")

$venvPython = Get-VenvPython -Root $Root
$appVersion = (& $venvPython -c "from src.version import APP_VERSION; print(APP_VERSION)").Trim()

& (Join-Path $Root "scripts\build_release.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$iscc = Get-InnoSetupCompiler
if (-not $iscc) {
    Write-Host "Inno Setup을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "설치: winget install JRSoftware.InnoSetup" -ForegroundColor Yellow
    exit 1
}

Write-Host "Inno Setup: $iscc"
Write-Host "설치 패키지 빌드 중 (v$appVersion)..."
& $iscc (Join-Path $Root "installer\quickpaste.iss")
if ($LASTEXITCODE -ne 0) {
    Write-Host "Inno Setup 빌드 실패 (exit $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

$setupName = "QuickPasteManager-Setup-$appVersion.exe"
$setup = Join-Path $Root "dist\$setupName"
if (-not (Test-Path $setup)) {
    Write-Host "설치 exe를 찾지 못했습니다: $setup" -ForegroundColor Yellow
    exit 1
}

# 포터블 ZIP (데이터 미포함)
$portableDir = Join-Path $Root "dist\QuickPasteManager"
$portableZip = Join-Path $Root "dist\QuickPasteManager-$appVersion-portable.zip"
if (Test-Path $portableZip) { Remove-Item $portableZip -Force }
Compress-Archive -Path $portableDir -DestinationPath $portableZip -CompressionLevel Optimal

# 테스트용 샘플 ZIP — 설치본과 별도 배포 (앱 번들에 포함하지 않음)
$sampleZip = Get-ChildItem (Join-Path $Root "samples") -Filter "HanbitSolutions_*.zip" -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($sampleZip) {
    $sampleDest = Join-Path $Root "dist\$($sampleZip.Name)"
    Copy-Item -Force $sampleZip.FullName $sampleDest
    Write-Host "샘플 데이터(별도): $sampleDest"
} else {
    Write-Host "samples\HanbitSolutions_*.zip 없음 — generate_sample_import_zip.py 실행 권장" -ForegroundColor Yellow
}

# 제출용 폴더에 설치 파일 복사
$submitDir = Join-Path $Root "제출용자료"
if (Test-Path $submitDir) {
    Copy-Item -Force $setup (Join-Path $submitDir $setupName)
}

Write-Host ""
Write-Host "배포 산출물 (v$appVersion):" -ForegroundColor Green
Write-Host "  설치: $setup ($([math]::Round((Get-Item $setup).Length / 1MB, 2)) MB)"
Write-Host "  포터블: $portableZip ($([math]::Round((Get-Item $portableZip).Length / 1MB, 2)) MB)"
if ($sampleZip) {
    Write-Host "  샘플 ZIP: dist\$($sampleZip.Name) (트레이 → 불러오기)"
}
Write-Host ""
Write-Host "첫 실행 시 DB는 비어 있으며 기본 카테고리 5개만 생성됩니다."
Write-Host "기존 PC에 테스트 데이터가 보이면 %APPDATA%\QuickPasteManager 를 삭제 후 재설치하세요."
