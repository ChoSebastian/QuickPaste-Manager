# QuickPaste Manager PRD v3

| 항목 | 내용 |
|------|------|
| 문서 버전 | 3.0 |
| 작성일 | 2026-05-31 |
| 제품명 | QuickPaste Manager |
| 플랫폼 | Windows 10/11 (64-bit) |
| 기술 스택 | Python 3.12+, PySide6 6.6+, SQLite3, pywin32, Pillow |
| 앱 버전 | 0.2.0 |

---

## 1. 제품 정의

텍스트·이미지 상용구를 **카테고리별 로컬 저장**하고, **RegisterHotKey 전역 단축키**로 **커서 인접 팝업**을 연 뒤 **클립보드 + SendInput Ctrl+V**로 붙여넣는 **트레이 상주 데스크톱 유틸리티**.

**비목표:** Shell Extension, 클라우드, 팀 기능, AI, 암호화, 마우스 휠 트리거(설정 키는 deprecated, UI 없음).

---

## 2. 목표

| ID | 목표 | v3 |
|----|------|-----|
| G1 | 전역 단축키 팝업 호출 | ✅ |
| G2 | 텍스트·이미지 상용구 관리 | ✅ |
| G3 | Top 5 / 카테고리 / 검색 UX | ✅ |
| G4 | 이미지 미리보기·원본 열기 | ✅ |
| G5 | 붙여넣기 실패 시 팝업 유지 | ✅ |
| G6 | ZIP Import/Export | ✅ |
| G7 | 자동 백업 | ✅ |
| G8 | Windows 시작 프로그램 | ✅ |
| G9 | 설치 패키지(PyInstaller+Inno) | ✅ |
| G10 | 단일 인스턴스 | ✅ |

---

## 3. 사용자·데이터

- **사용자:** Windows 로그인 사용자 1인, RBAC 없음
- **데이터:** `%APPDATA%\QuickPasteManager` (DB, assets, settings, logs, backups, exports)

---

## 4. 기능 요구사항

### 4.1 Must (v3 구현)

| ID | 요구사항 |
|----|----------|
| FR-01 | 시스템 트레이: 팝업, 관리, 환경설정, 보내기, 불러오기, 도움말, 종료 |
| FR-02 | 전역 단축키 기본 **`Ctrl+Shift+Q`**, 충돌 시 fallback (`Ctrl+Shift+V`, `Ctrl+Alt+V`, …) |
| FR-03 | 환경설정 열림 시 단축키 suppress·팝업 미호출 |
| FR-04 | 단일 인스턴스; 재실행 시 기존 인스턴스 활성화 |
| FR-05 | 커서 인접 팝업, 최상위, 드래그, Esc/✕ 닫기 |
| FR-06 | Top 5 오버 → 우측 상세; 클릭 붙여넣기 |
| FR-07 | 카테고리 **클릭** → 우측 목록; 오버 → 하단 내용 |
| FR-08 | 검색 시 Top 5 영역에 결과 |
| FR-09 | 관리창 CRUD, 휴지통, 이미지(파일·클립보드) |
| FR-10 | 이미지 미리보기 클릭 → 원본 열기(팝업 유지) |
| FR-11 | 붙여넣기 **실패** 시 경고·팝업 유지 |
| FR-12 | `close_popup_after_paste` 기본 **false** — 연속 붙여넣기 |
| FR-13 | usage_events·Top 5 점수(핀·빈도) |
| FR-14 | 클립보드 Unicode + CF_TEXT(mbcs); SendInput; 전경 HWND 복원 |
| FR-15 | ZIP Export/Import (manifest v1) |
| FR-16 | 자동 백업(주기·keep count) |
| FR-17 | Windows 시작 프로그램(기본 ON) |
| FR-18 | 환경설정: 단축키 캡처, probe, 토글 UI |
| FR-19 | 도움말 HTML 창(동적 단축키 표시) |
| FR-20 | 팝업 하단 → 관리/설정 연동 |

### 4.2 Won't / Removed (v3)

| ID | 항목 |
|----|------|
| FR-X1 | 마우스 휠·가운데 버튼 호출 UI/연동 |
| FR-X2 | 테마·글자 크기 설정 |
| FR-X3 | Shell Extension |

### 4.3 Could (이후)

| ID | 항목 |
|----|------|
| FR-30 | 팝업 크기 설정 UI |
| FR-31 | 태그 필터 고도화 |
| FR-32 | 다국어 UI |

---

## 5. 사용자 스토리 (발췌)

### US-01 호출

> **As a** 사용자, **I want** `Ctrl+Shift+Q`로 팝업을 열고, **so that** 작업 앱 옆에서 상용구를 고른다.

**AC:** 300ms 내 체감 표시; 최상위; 설정 창 열림 시 단축키로 팝업 안 열림; `close_popup_after_paste` OFF면 외부 클릭해도 팝업 유지.

### US-02 단축키 변경

> **I want** 환경설정에서 단축키를 바꾸고, **현재 쓰는 조합**을 다시 넣어도 오류가 나지 않게 한다.

**AC:** 창 열 때 저장값 표시; 클릭 후 입력; blur 시 미변경 복원; `probe_available`이 자기 등록 키는 통과.

### US-03 데이터 이전

> **I want** ZIP으로 상용구를 백업·복원한다.

**AC:** manifest.json v1; 카테고리·상용구·assets·선택적 settings 병합.

---

## 6. 비기능 요구사항

| ID | 항목 | 요구 |
|----|------|------|
| NFR-01 | OS | Win10/11 x64 |
| NFR-02 | 성능 | 팝업 preload(`_ensure_popup`) |
| NFR-03 | DB | SQLite, FK, 인덱스 |
| NFR-04 | 로그 | rotating file |
| NFR-05 | 테스트 | pytest 76+ (2026-05 기준) |
| NFR-06 | 보안 | 로컬만, 네트워크 전송 없음 |
| NFR-07 | 패키징 | PyInstaller one-folder + Inno optional |

---

## 7. 데이터 모델

| 엔티티 | 핵심 필드 |
|--------|-----------|
| Category | name(UNIQUE), sort_order, color, active |
| Asset | stored_path, mime, sha256, width, height |
| Snippet | category_id, title, content_type, body_text, asset_id, tags, pinned, use_count, active |
| UsageEvent | snippet_id, success, error_code, target_* |

스키마: `src/repositories/db.py` — `SCHEMA_SQL`

---

## 8. 설정 (`settings.json`)

| 키 | 기본값 | UI | 설명 |
|----|--------|-----|------|
| `version` | 1 | — | 설정 스키마 |
| `hotkey` | **Ctrl+Shift+Q** | ✅ | `DEFAULT_HOTKEY` |
| `startup_with_windows` | true | ✅ | 시작 프로그램 |
| `popup_offset_px` | 12 | ✅ | 커서 보정 |
| `popup_width` | 360 | — | 코드만 |
| `popup_height` | 520 | — | 코드만 |
| `paste_delay_ms` | 50 | ✅ | 붙여넣기 지연 |
| `restore_clipboard_after_paste` | true | ✅ | |
| `close_popup_after_paste` | **false** | ✅ | |
| `auto_backup_interval_hours` | 24 | ✅ | |
| `auto_backup_keep_count` | 10 | — | 스케줄러 |
| `seed_default_categories` | true | — | 최초 DB |
| `seed_sample_snippets` | false | — | |
| `mouse_wheel_trigger_enabled` | false | — | **deprecated** |
| `image_paste_mode` | clipboard | — | **미사용** |

---

## 9. 제약

- 일반 사용자 권한; 일부 관리자 권한 앱은 SendInput 실패 가능
- 다중 모니터: 커서 기준 배치
- 한글: cp949 호환을 위해 CF_TEXT 동시 설정

---

## 10. 릴리스 기준 (v0.2.0)

- [x] `pytest` 전체 통과
- [x] Top5·카테고리·이미지·텍스트 시나리오
- [x] Import/Export·백업
- [x] 설치 파일 빌드 스크립트
- [ ] 비개발자 PC 대량 호환성(계획: `compatibility-test-plan.md`)

---

## 11. 관련 문서

- [기획서_v3.md](./기획서_v3.md)
- [기능명세서_v3.md](./기능명세서_v3.md)
- [cursor_kickoff_v3.md](./cursor_kickoff_v3.md)

| 버전 | 일자 | 변경 |
|------|------|------|
| 2.0 | 2026-06-01 | 팝업·이미지 |
| 3.0 | 2026-05-31 | 배포·설정·데이터·단축키 정합 |
