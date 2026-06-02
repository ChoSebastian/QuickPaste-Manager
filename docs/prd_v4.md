# QuickPaste Manager PRD v4

| 항목 | 내용 |
|------|------|
| 문서 버전 | 4.0 |
| 작성일 | 2026-05-31 |
| 제품명 | QuickPaste Manager |
| 플랫폼 | Windows 10/11 (64-bit) |
| 기술 스택 | Python 3.12+, PySide6 6.6+, SQLite3, pywin32, Pillow |
| 앱 버전 | 0.2.3 |

---

## 1. 제품 정의

텍스트·이미지 상용구를 **카테고리별 로컬 저장**하고, **RegisterHotKey**로 **커서 인접 팝업**을 연 뒤 **클립보드(Win+V 미기록) + SendInput Ctrl+V**로 붙여넣는 **트레이 상주 데스크톱 유틸리티**.

---

## 2. 목표

| ID | 목표 | v4 |
|----|------|-----|
| G1 | 전역 단축키 팝업 | ✅ |
| G2 | 텍스트·이미지 관리 | ✅ |
| G3 | Top 5 / 카테고리 / 검색 | ✅ |
| G4 | 이미지 미리보기·원본 열기 | ✅ |
| G5 | 붙여넣기 실패 시 팝업 유지 | ✅ |
| G6 | ZIP Import/Export | ✅ |
| G7 | 자동 백업 | ✅ |
| G8 | Windows 시작 프로그램 | ✅ |
| G9 | 설치 패키지 | ✅ 0.2.2 |
| G10 | 단일 인스턴스 | ✅ |
| G11 | **카테고리 우측 상세·목록 유지** | ✅ v4 |
| G12 | **유지 모드 다중 창 붙여넣기** | ✅ v4 |
| G13 | **Win+V 클립보드 히스토리 미축적** | ✅ v4 |

---

## 3. 사용자·데이터

- **사용자:** Windows 로그인 사용자 1인
- **데이터:** `%APPDATA%\QuickPasteManager`

---

## 4. 기능 요구사항

### 4.1 Must (v4 구현)

| ID | 요구사항 |
|----|----------|
| FR-01 ~ FR-20 | v3 Must 전부 (트레이, 핫키, 팝업, CRUD, ZIP, 백업, 도움말 등) |
| FR-21 | 카테고리 클릭 → 우측 **목록** `SnippetFlyout` |
| FR-22 | 목록 오버 → 목록 **우측** `SnippetDetailFlyout` (제목 「상용구 전체 내용」) |
| FR-23 | 카테고리 목록은 **헤더 ×**·메인 닫기·검색·카테고리 전환·`close_popup_after_paste` ON 성공 시에만 닫힘 |
| FR-24 | `close_popup_after_paste` **false** 시 붙여넣기 성공 후 메인·카테고리 목록·상세 **유지** |
| FR-25 | `close_popup_after_paste` **false** 시 커서/전경 기준 **외부 HWND 갱신** (`capture_window_at_cursor`, 100ms 폴링) |
| FR-26 | 클립보드 설정 전 `ExcludeClipboardContentFromMonitorProcessing` (텍스트·이미지) |
| FR-27 | 우리 팝업 HWND 집합에 카테고리 상세 창 포함 (`auxiliary_hwnds`) |
| FR-28 | 카테고리 목록 열림 중 Top 5 오버 → Top 5 상세를 **목록 창 우측·최상위**; 목록 유지; Top 5 상세는 **리스트 영역 이탈 시** 닫힘 |

### 4.2 Won't / Removed

v3와 동일: 마우스 휠 UI, 테마, Shell Extension.

### 4.3 Could (이후)

| ID | 항목 |
|----|------|
| FR-30 | 팝업 크기 설정 UI |
| FR-31 | 코드 서명·SAC 대응 |
| FR-32 | UI 목업 v4 캡처 갱신 |

---

## 5. 사용자 스토리 (v4 추가)

### US-04 카테고리 연속 붙여넣기

> **As a** 사용자, **I want** 카테고리 목록을 연 채로 여러 항목을 다른 창에 붙여넣고, **so that** 목록을 다시 열 필요가 없다.

**AC:**

- 목록 창이 마우스 이탈로 닫히지 않음
- `close_popup_after_paste` OFF 시 붙여넣기 후 목록·상세 유지
- Word → Notepad 등 창 전환 후에도 올바른 창에 붙여넣기

### US-05 Win+V

> **I want** 상용구 붙여넣기가 Windows 클립보드 히스토리(Win+V)에 남지 않게 한다.

**AC:** `set_unicode_text`·이미지 클립보드 설정 직전 제외 API 호출; 복원 시에도 동일 경로.

### US-06 Top 5 빠른 붙여넣기 (카테고리 목록 열림)

> **I want** 카테고리 목록을 연 채로 Top 5를 잠깐 붙여넣고, **so that** 목록을 다시 열지 않아도 된다.

**AC:** Top 5 상세가 목록 창 위·우측에 표시; 클릭 붙여넣기; Top 5 상세는 마우스가 Top 5 영역을 벗어날 때 닫힘; 카테고리 목록 유지.

---

## 6. 비기능 요구사항

| ID | 항목 | v4 |
|----|------|-----|
| NFR-01 | OS | Win10/11 x64 |
| NFR-05 | 테스트 | pytest **83+** (2026-05-31) |
| NFR-08 | 클립보드 | Win+V 제외 (API 가용 시) |

---

## 7. 설정 (`settings.json`)

v3와 동일. 핵심:

| 키 | 기본값 |
|----|--------|
| `hotkey` | Ctrl+Shift+Q |
| `close_popup_after_paste` | **false** |
| `restore_clipboard_after_paste` | true |

---

## 8. 릴리스 기준 (v0.2.3 마감)

- [x] `pytest` 전체 통과
- [x] 카테고리·Top 5 교차 UX (목록 열림 + Top 5 호버)
- [x] 유지 모드 다중 창·Win+V 제외
- [x] GitHub Release v0.2.3

---

## 9. 관련 문서

- [기획서_v4.md](./기획서_v4.md)
- [기능명세서_v4.md](./기능명세서_v4.md)
- [cursor_kickoff_v4.md](./cursor_kickoff_v4.md)

| 버전 | 일자 | 변경 |
|------|------|------|
| 3.0 | 2026-05-31 | 배포·설정 |
| 4.0 | 2026-05-31 | 배포·설정 |
| 4.1 | 2026-05-31 | v0.2.3 최종 — 카테고리+Top5 교차 UX |
