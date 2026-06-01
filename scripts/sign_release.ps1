# QuickPaste Manager — Authenticode 서명 (선택, 인증서 필요)
# 사용 전: dist\QuickPasteManager 가 build_release.ps1 로 이미 빌드되어 있어야 함.
#
# 환경 변수:
#   QPM_SIGN_PFX      — PFX 파일 경로 (필수)
#   QPM_SIGN_PASSWORD — PFX 비밀번호 (선택, 없으면 프롬프트)
#   QPM_TIMESTAMP_URL — 기본 http://timestamp.digicert.com
#
# 예:
#   $env:QPM_SIGN_PFX = "D:\certs\codesign.pfx"
#   $env:QPM_SIGN_PASSWORD = "secret"
#   .\scripts\sign_release.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

$pfx = $env:QPM_SIGN_PFX
if (-not $pfx -or -not (Test-Path $pfx)) {
    Write-Host "QPM_SIGN_PFX 환경 변수에 유효한 .pfx 경로를 설정하세요." -ForegroundColor Red
    Write-Host "Smart App Control 대응: docs/deploy.md 의 '코드 서명' 절을 참고하세요."
    exit 1
}

$signtool = Get-Command signtool.exe -ErrorAction SilentlyContinue
if (-not $signtool) {
    Write-Host "signtool.exe 를 찾을 수 없습니다. Windows SDK 또는 Visual Studio Build Tools 를 설치하세요." -ForegroundColor Red
    exit 1
}

$ts = if ($env:QPM_TIMESTAMP_URL) { $env:QPM_TIMESTAMP_URL } else { "http://timestamp.digicert.com" }
$passArg = @()
if ($env:QPM_SIGN_PASSWORD) {
    $passArg = @("/p", $env:QPM_SIGN_PASSWORD)
}

$portableDir = Join-Path $Root "dist\QuickPasteManager"
if (-not (Test-Path (Join-Path $portableDir "QuickPasteManager.exe"))) {
    Write-Host "먼저 .\scripts\build_release.ps1 를 실행하세요." -ForegroundColor Red
    exit 1
}

$files = Get-ChildItem $portableDir -Recurse -File |
    Where-Object { $_.Extension -match '^\.(exe|dll|pyd)$' }

Write-Host "서명 대상: $($files.Count) 파일"
foreach ($f in $files) {
    Write-Host "  $($f.FullName)"
    & $signtool sign /fd SHA256 /tr $ts /td SHA256 /f $pfx @passArg $f.FullName
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$setup = Get-ChildItem (Join-Path $Root "dist") -Filter "QuickPasteManager-Setup-*.exe" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($setup) {
    Write-Host "설치 프로그램 서명: $($setup.FullName)"
    & $signtool sign /fd SHA256 /tr $ts /td SHA256 /f $pfx @passArg $setup.FullName
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "서명 완료. Smart App Control 환경에서 재설치 테스트하세요." -ForegroundColor Green
