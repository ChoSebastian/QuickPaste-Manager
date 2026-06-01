# QuickPaste Manager

Windows에서 자주 쓰는 **텍스트·이미지 상용구**를 저장하고, 전역 단축키로 커서 근처 팝업을 열어 즉시 붙여넣을 수 있게 해주는 **상주형 생산성 유틸리티**입니다.

> Shell Extension(우클릭 메뉴)이 아니라 **글로벌 호출 → 자체 팝업 → 클립보드 등록 → SendInput Ctrl+V** 흐름으로 동작합니다.

**저장소:** [github.com/ChoSebastian/QuickPaste-Manager](https://github.com/ChoSebastian/QuickPaste-Manager)

---

## 주요 기능

| 영역 | 설명 |
|------|------|
| 시스템 트레이 | 상주 실행, 팝업·관리·설정·종료 |
| 전역 단축키 | `RegisterHotKey` (기본 `Ctrl+Shift+V`, 충돌 시 fallback) |
| 메인 팝업 | 검색, Top 5, 카테고리, 커서 인접·최상위·드래그 이동 |
| Top 5 | 2줄 축약 목록 → 오버 시 우측 **전체 내용** 패널 |
| 카테고리 | **클릭** 시 우측 상용구 목록 → 오버 시 하단 **전체 내용** |
| 이미지 | 썸네일, 미리보기 **클릭 시 원본 열기**, 클립보드 붙여넣기 |
| 관리창 | 카테고리·상용구 CRUD, 휴지통, 클립보드/파일 이미지 추가 |
| 데이터 | 로컬 SQLite + `%APPDATA%\QuickPasteManager` |

### 구현 상태 (v2)

| 기능 | 상태 |
|------|------|
| 전역 단축키 | ✅ |
| 텍스트 붙여넣기 (Unicode+ANSI, SendInput) | ✅ |
| 이미지 붙여넣기 | ✅ |
| 붙여넣기 실패 시 팝업 유지 | ✅ |
| 이미지 미지원 대상 경고 (메모장·Edit 등) | ✅ |
| 팝업 UI (목업 QSS, 보조 패널) | ✅ |
| 관리창 CRUD·휴지통 | ✅ |
| 마우스 가운데 버튼 호출 | ✅ |
| Import / Export (ZIP) | ✅ |
| 자동 백업 (주기·보관 개수) | ✅ |
| Windows 시작 시 실행 | ✅ |
| 설치 패키지 (PyInstaller + Inno) | 🔶 `scripts\build_release.ps1` |

---

## 빠른 사용법

1. `.\scripts\dev_run.ps1` 실행 → 트레이 아이콘 확인
2. 작업 중인 앱에서 **단축키** (환경설정에서 변경 가능, 예: `Ctrl+Shift+Q`)
3. **Top 5**: 항목에 마우스 오버 → 우측에서 내용 확인 → 항목 **클릭**으로 붙여넣기
4. **카테고리**: 카테고리 **클릭** → 우측 목록 → 오버로 내용 확인 → 항목 **클릭**으로 붙여넣기
5. **이미지 미리보기**: 이미지를 **클릭**하면 원본 파일이 열리며 팝업은 유지됨
6. 상용구 등록·수정: 트레이 → **상용구 관리**

---

## 개발 환경

| 항목 | 버전 |
|------|------|
| OS | Windows 10/11 64-bit |
| Python | 3.12+ |
| GUI | PySide6 |
| DB | SQLite3 |

---

## 설치 및 실행

> **Windows Store `python` 스텁 주의:** `WindowsApps\python.exe`만 있으면 실제 Python이 없을 수 있습니다.  
> `winget install Python.Python.3.12` 또는 [python.org](https://www.python.org/downloads/)에서 설치하세요.

```powershell
cd "D:\Smit_Dev\Python\QuickPaste Manager"

# 1) 부트스트랩 (Python 탐색 + venv + 의존성)
.\scripts\bootstrap.ps1

# 2) 실행
.\scripts\dev_run.ps1
```

수동 실행:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main
```

배포용 설치 파일 (Windows):

```powershell
# 최초: winget install JRSoftware.InnoSetup  (또는 installer\build_installer.ps1 안내 참고)
.\installer\build_installer.ps1
# 산출물: dist\QuickPasteManager-Setup-0.2.0.exe
```

포터블 실행만 필요하면 `.\scripts\build_release.ps1` → `dist\QuickPasteManager\`

자세한 내용: [docs/deploy.md](docs/deploy.md)

---

## 테스트

```powershell
.\.venv\Scripts\Activate.ps1
pytest
```

이미지·붙여넣기·팝업 관련만:

```powershell
pytest tests/test_image_snippet.py tests/test_popup_window.py tests/test_paste_service.py -q
```

---

## 폴더 구조

```text
QuickPaste Manager/
├─ src/
│  ├─ main.py
│  ├─ app/                    # AppController, 트레이
│  ├─ ui/
│  │  ├─ popup_window.py      # 메인 팝업
│  │  ├─ manager_window.py     # 상용구 관리
│  │  ├─ settings_window.py
│  │  └─ widgets/             # flyout, detail, 이미지 미리보기 등
│  ├─ services/               # hotkey, clipboard, paste
│  ├─ repositories/
│  ├─ models/
│  ├─ utils/
│  └─ resources/              # icons, popup.qss
├─ tests/
├─ docs/                      # v2 기획·PRD·명세, UI 목업
├─ doc/                       # v1 원본 기획
├─ scripts/
└─ installer/                 # (예정)
```

---

## 로컬 데이터

```text
%APPDATA%\QuickPasteManager\
├─ app.db
├─ settings.json
├─ assets/          # 이미지 파일
├─ logs/
├─ exports/
└─ backups/
```

---

## Git / GitHub

```powershell
git clone https://github.com/ChoSebastian/QuickPaste-Manager.git
cd QuickPaste-Manager
.\scripts\bootstrap.ps1
.\scripts\dev_run.ps1
```

변경 사항 push:

```powershell
git add .
git commit -m "메시지"
git push origin main
```

---

## 제한사항

- 릴리스 빌드: `.\scripts\build_release.ps1` (Inno Setup은 `installer\build_installer.ps1`)
- 메모장 등 텍스트 전용 창에는 이미지 붙여넣기 불가 (사전 경고)
- 붙여넣기 **실패 시** 팝업은 닫히지 않고 경고만 표시
- 관리자 권한 프로세스 등 일부 앱에서는 SendInput이 차단될 수 있음
- 팝업 하단 추가/수정/삭제/설정 버튼은 관리창 연동 전까지 비활성

---

## 문서

### v2 (현재 구현 기준, 권장)

- [기획서 v2](docs/기획서_v2.md)
- [PRD v2](docs/prd_v2.md)
- [기능명세서 v2](docs/기능명세서_v2.md)

### 참고

- [아키텍처 개요](docs/architecture.md)
- [UI 목업](docs/기본ui-1.png) · [플라이아웃 목업](docs/기본ui-2.png)
- [호환성 테스트 계획](docs/compatibility-test-plan.md)
- [릴리스 체크리스트](docs/release-checklist.md)
- [PRD v1](docs/quickpaste-manager-prd.md) · [원본 기획](doc/02.%20quickpaste_manager_prd_final.md)

---

## 로드맵

1. Import / Export ZIP
2. 마우스 휠 클릭 호출
3. 팝업 ↔ 관리창 단축 연동
4. PyInstaller + Inno Setup 설치 패키지

---

## 라이선스

MIT (예정)
