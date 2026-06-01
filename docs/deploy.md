# 배포(설치 파일) 만들기

## 필요한 소프트웨어

| 도구 | 용도 | 설치 |
|------|------|------|
| Python 3.12+ | 개발·빌드 | [python.org](https://www.python.org/downloads/) 또는 `winget install Python.Python.3.12` |
| PyInstaller | 실행 파일 패키징 | `bootstrap.ps1` 시 venv에 자동 설치 |
| Inno Setup 6 | Windows 설치 프로그램 | `winget install JRSoftware.InnoSetup` |

## 한 번에 빌드

```powershell
cd "D:\Smit_Dev\Python\QuickPaste Manager"

# 1) 가상환경·의존성 (최초 1회)
.\scripts\bootstrap.ps1

# 2) 실행 파일 + 설치 패키지
.\installer\build_installer.ps1
```

## 산출물

| 경로 | 설명 |
|------|------|
| `dist\QuickPasteManager\QuickPasteManager.exe` | 포터블(one-folder) 실행 |
| `dist\QuickPasteManager-Setup-0.2.2.exe` | 배포용 설치 프로그램 (상용구 미포함) |
| `dist\HanbitSolutions_상용구샘플_200.zip` | 별도 샘플 Import ZIP |

설치 후 데이터는 `%APPDATA%\QuickPasteManager`에 저장됩니다.

## PyInstaller만 (설치 파일 없이)

```powershell
.\scripts\build_release.ps1
```

---

## Windows Smart App Control(SAC) / Defender 차단

### 왜 막히나요?

현재 `QuickPasteManager-Setup-0.2.2.exe`는 **Authenticode 코드 서명이 없고**, Microsoft 클라우드 **평판(reputation)도 없는** 신규 실행 파일입니다.

Windows 11 **Smart App Control**이 켜져 있으면:

- 서명이 없거나 평판이 없는 `.exe`·`.dll`·설치 프로그램을 **차단**할 수 있습니다.
- SmartScreen의 「추가 정보 → 실행」과 달리, SAC **강제 모드**에서는 앱별 예외가 **없을 수** 있습니다.

PyInstaller 산출물은 `QuickPasteManager.exe`뿐 아니라 `_internal` 아래 **수십 개 DLL**도 함께 검사 대상입니다.

### 근본 해결 (배포자 — 권장)

| 방법 | 설명 | 비용·난이도 |
|------|------|-------------|
| **1. 코드 서명** | 신뢰 CA 인증서로 **설치 exe + 모든 exe/dll** 서명 + 타임스탬프 | OV 연 ~$200/년, EV는 더 비쌈·평판 유리 |
| **2. Microsoft Trusted Signing** | Microsoft 클라우드 코드 서명 서비스 ([문서](https://learn.microsoft.com/azure/trusted-signing/)) | 개발자 등록·구독 |
| **3. Microsoft Store** | Store 배포 시 SAC 우회 | 심사·수수료 |
| **4. 평판 구축** | 서명 후 배포 → [Microsoft Security Intelligence](https://www.microsoft.com/wdsi/filesubmission)에 **정상 소프트웨어** 제출 | 시간 소요 |

서명 시 **반드시**:

1. `dist\QuickPasteManager\` 안의 `QuickPasteManager.exe` 및 `_internal\**\*.dll`, `*.pyd`
2. `dist\QuickPasteManager-Setup-0.2.2.exe` (설치 프로그램)

모두 같은 인증서로 서명하고 **RFC3161 타임스탬프**를 붙입니다.

인증서(PFX)가 있으면 (선택):

```powershell
$env:QPM_SIGN_PFX = "C:\certs\codesign.pfx"
$env:QPM_SIGN_PASSWORD = "비밀번호"
.\scripts\sign_release.ps1
.\installer\build_installer.ps1   # 서명 후 Inno 재빌드는 보통 설치본만 다시
```

또는 Inno Setup `[Setup] SignTool` / `SignedUninstaller=yes` 설정 ([Inno Setup 문서](https://jrsoftware.org/ishelp/index.php?topic=setup_signtool)).

### 최종 사용자 임시 조치 (배포 안내용)

개발·사내 테스트 PC 등에서만:

1. **설정 → 개인 정보 보호 및 보안 → Windows 보안 → 앱 및 브라우저 컨트롤**
2. **Smart App Control** → **끔** (또는 평가 모드 종료 후 끔)
3. 설치 후 필요 시 다시 켬

또는 **Windows 보안 → 바이러스 및 위협 방지 → 허용된 위협**에서 차단 항목 복원(Defender만 걸린 경우).

> SAC를 끄지 않고 배포하려면 **코드 서명이 사실상 필수**에 가깝습니다.

### SmartScreen만 뜨는 경우 (SAC 아님)

- 다운로드 직후: 파일 우클릭 → **속성** → **차단 해제** → 적용 후 설치
- 또는 서명·평판 확보 후 재배포
