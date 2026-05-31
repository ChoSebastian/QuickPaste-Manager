# QuickPaste Manager

Windows에서 자주 쓰는 **텍스트·이미지 상용구**를 저장하고, 전역 단축키 또는 마우스 트리거로 커서 근처 팝업을 열어 즉시 붙여넣을 수 있게 해주는 **상주형 생산성 유틸리티**입니다.

> 우클릭 메뉴(Shell Extension) 방식이 아니라, **글로벌 호출 → 자체 팝업 → 클립보드 등록 → 자동 붙여넣기** 흐름으로 동작합니다.

---

## 주요 기능 범위 (PRD 기준)

| 포함 | 제외 |
|------|------|
| 시스템 트레이 상주 | 클라우드 동기화 |
| 전역 단축키 / 마우스 휠 호출 | 팀/계정 기능 |
| 커서 인접 팝업 | AI 기능 |
| 텍스트·이미지 상용구 관리 | Shell Extension |
| 카테고리 / 검색 / Top 5 | |
| Import / Export (ZIP) | |
| 로컬 SQLite + AppData 저장 | |

현재 착수 단계에서는 **실행 가능한 골격**만 구현되어 있으며, 전역 단축키·자동 붙여넣기·이미지 클립보드 등은 TODO로 남겨 두었습니다.

---

## 개발 환경

- **OS:** Windows 10/11 64-bit
- **Python:** 3.12+
- **GUI:** PySide6
- **DB:** SQLite3
- **패키징 목표:** PyInstaller + Inno Setup

---

## 설치 방법

```powershell
cd "D:\Smit_Dev\Python\QuickPaste Manager"

# 가상환경 생성 (권장)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt
```

또는 부트스트랩 스크립트:

```powershell
.\scripts\bootstrap.ps1
```

---

## 개발 실행 방법

```powershell
cd "D:\Smit_Dev\Python\QuickPaste Manager"
.\.venv\Scripts\Activate.ps1
python -m src.main
```

또는:

```powershell
.\scripts\dev_run.ps1
```

실행 후 **시스템 트레이**에 아이콘이 표시됩니다. 트레이 메뉴에서 팝업/관리/설정 창을 열 수 있습니다.

---

## 테스트

```powershell
pytest
```

---

## 폴더 구조

```text
QuickPaste Manager/
├─ src/
│  ├─ main.py                 # 진입점
│  ├─ app/                    # 앱·트레이·재시작 컨트롤러
│  ├─ ui/                     # 팝업 / 관리 / 설정 창
│  ├─ services/               # hotkey, clipboard, paste 등
│  ├─ repositories/           # SQLite 접근
│  ├─ models/                 # 데이터 모델
│  ├─ utils/                  # paths, config, logger
│  └─ resources/              # 아이콘, 스타일
├─ tests/
├─ docs/                      # PRD, 아키텍처 문서
├─ doc/                       # 원본 기획 문서
├─ scripts/                   # bootstrap, dev_run
├─ installer/                 # Inno Setup (예정)
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

---

## 로컬 데이터 저장 위치

앱 실행 시 다음 경로가 자동 생성됩니다.

```text
%APPDATA%\QuickPasteManager\
├─ app.db
├─ settings.json
├─ assets/
├─ logs/
├─ exports/
└─ backups/
```

---

## Git / GitHub 연결 방법

원격 저장소: [https://github.com/ChoSebastian/QuickPaste-Manager.git](https://github.com/ChoSebastian/QuickPaste-Manager.git)

### 1. Git 초기화 (최초 1회)

```powershell
cd "D:\Smit_Dev\Python\QuickPaste Manager"
git init
git branch -M main
```

### 2. 초기 커밋

```powershell
git add .
git commit -m "Initial project scaffold"
```

### 3. 원격 연결 및 push

```powershell
git remote add origin https://github.com/ChoSebastian/QuickPaste-Manager.git
git push -u origin main
```

> **참고:** `git push` 시 GitHub 로그인 또는 Personal Access Token 인증이 필요합니다.  
> 이미 `origin`이 등록되어 있다면 `git remote set-url origin <URL>` 로 변경하세요.

---

## 향후 구현 예정 (Phase 2~)

1. RegisterHotKey 기반 전역 단축키
2. SendInput 기반 자동 Ctrl+V 붙여넣기
3. 이미지 클립보드 (Windows DIB/CF_BITMAP)
4. Import/Export ZIP 패키지
5. PyInstaller + Inno Setup 설치 파일

---

## 제한사항 (착수 단계)

- 전역 단축키·마우스 훅은 **stub** 상태
- 자동 붙여넣기는 클립보드 등록까지만 동작
- 이미지 붙여넣기 미구현
- Import/Export 미구현
- 설치 마법사·시작 프로그램 등록 미구현

---

## 문서

- [PRD (최종)](docs/quickpaste-manager-prd.md)
- [아키텍처 개요](docs/architecture.md)
- [호환성 테스트 계획](docs/compatibility-test-plan.md)
- [릴리스 체크리스트](docs/release-checklist.md)

---

## 라이선스

MIT (예정)
