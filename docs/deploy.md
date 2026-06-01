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
| `dist\QuickPasteManager-Setup-0.2.0.exe` | 배포용 설치 프로그램 |

설치 후 데이터는 `%APPDATA%\QuickPasteManager`에 저장됩니다.

## PyInstaller만 (설치 파일 없이)

```powershell
.\scripts\build_release.ps1
```
