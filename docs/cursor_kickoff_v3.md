# Cursor 개발 착수본 v3 — QuickPaste Manager

> **목적:** 이 문서만으로도 현재 저장소와 **동일한 형태**의 Windows 상용구 유틸리티를 구현할 수 있도록, 코드와 대조한 **단일 소스 착수 지시서**를 제공한다.  
> 상세 화면 규칙은 [기능명세서_v3.md](./기능명세서_v3.md), 요구사항은 [prd_v3.md](./prd_v3.md)를 참고한다.

| 항목 | 값 |
|------|-----|
| 문서 버전 | 3.0 |
| 작성일 | 2026-05-31 |
| 프로젝트 루트 | `D:\Smit_Dev\Python\QuickPaste Manager` (공백 경로 주의) |
| Python | 3.12+ |
| GUI | PySide6 >= 6.6 |
| DB | SQLite3 |
| OS | Windows 10/11 x64 only (핫키·SendInput·트레이) |

---

## 1. Cursor 역할

1. 아래 **디렉터리·모듈·스키마·설정**을 그대로 재현한다.
2. PRD v3 **Must**만 구현한다. **Won't**(마우스 휠 UI, 테마 설정)는 넣지 않는다.
3. `pytest` 전체가 통과하도록 테스트를 유지·추가한다.
4. Windows 전용 API는 `sys.platform == "win32"` 분기 + Stub 서비스로 non-Windows에서 import 가능하게 한다.
5. 범위 밖 기능(클라우드, AI, Shell Extension)은 추가하지 않는다.

---

## 2. 실행·개발 명령

```powershell
cd "D:\Smit_Dev\Python\QuickPaste Manager"
.\scripts\bootstrap.ps1    # venv + pip install
.\scripts\dev_run.ps1        # python -m src.main
.\.venv\Scripts\python.exe -m pytest tests/ -q
.\scripts\build_release.ps1  # PyInstaller
.\installer\build_installer.ps1  # Inno Setup → dist\QuickPasteManager-Setup-0.2.0.exe
```

**의존성 (`requirements.txt`):** PySide6, pywin32, Pillow, pytest, pytest-qt

---

## 3. 디렉터리 구조 (필수)

```text
QuickPaste Manager/
├─ src/
│  ├─ main.py
│  ├─ app/           app_controller, tray_controller, backup_scheduler, restart_manager
│  ├─ ui/            popup, manager, settings, help, widgets/*
│  ├─ services/      hotkey, paste, clipboard, backup, import_export*, asset, mouse_trigger(미연결)
│  ├─ repositories/  db, category, snippet, asset, usage
│  ├─ models/        dataclass 4종
│  ├─ utils/         config, paths, single_instance, hotkey_*, input_injection, win_*, ...
│  └─ resources/     icons/, styles/popup.qss
├─ tests/            pytest + pytest-qt
├─ scripts/          bootstrap, dev_run, build_release, ...
├─ installer/        quickpaste.spec, quickpaste.iss, build_installer.ps1
├─ docs/             v3 문서 (본 파일 포함)
└─ samples/          HanbitSolutions_상용구샘플_200.zip 등
```

---

## 4. 진입점 동작 (`src/main.py`)

1. `QApplication`, `setQuitOnLastWindowClosed(False)`
2. 트레이 불가 시 critical 후 exit 1
3. `SingleInstanceGuard` — 비주: QMessageBox 후 return 0; 주: `AppController.start()`
4. `on_second_instance` → `controller.open_popup()`

---

## 5. AppController 핵심 (`src/app/app_controller.py`)

**생성 시:** `load_settings()`, `initialize_database(seed_default_categories)`, 서비스·스케줄러 생성.

**start():**

- `TrayController` show
- `_register_triggers()` — hotkey primary + FALLBACK_HOTKEYS
- `_ensure_popup()` preload
- `BackupScheduler.apply_settings`

**open_popup():**

- 설정 창 visible이면 return
- `popup.show_near_cursor(popup_offset_px, popup_width, popup_height)`

**open_settings():**

- `SettingsWindow(..., hotkey_probe_fn=service.probe_available, on_close=suppress off)`
- `set_suppressed(True)` before show

**_save_settings:** save json, paste delay/restore, `_reregister_triggers`, backup, `apply_startup_setting`

---

## 6. 설정 (`src/utils/config.py`)

```python
DEFAULT_HOTKEY = "Ctrl+Shift+Q"

DEFAULT_SETTINGS = {
    "version": 1,
    "hotkey": DEFAULT_HOTKEY,
    "mouse_wheel_trigger_enabled": False,  # deprecated, unused
    "startup_with_windows": True,
    "popup_offset_px": 12,
    "popup_width": 360,
    "popup_height": 520,
    "paste_delay_ms": 50,
    "restore_clipboard_after_paste": True,
    "close_popup_after_paste": False,
    "image_paste_mode": "clipboard",  # unused in code
    "auto_backup_interval_hours": 24,
    "auto_backup_keep_count": 10,
    "seed_default_categories": True,
    "seed_sample_snippets": False,
}
```

`load_settings` / `merge_settings` / `save_settings` — `%APPDATA%\QuickPasteManager\settings.json`

---

## 7. DB 스키마 (`src/repositories/db.py`)

테이블: `categories`, `assets`, `snippets`, `usage_events` — `SCHEMA_SQL` 그대로 구현.

시드 카테고리 5개: 일반, 고객응대, 이메일, 계좌/연락처, 기타.

휴지통: `snippets.active = 0` (별도 테이블 없음).

Top 5: `snippet_repository.top_snippets` — pinned 우선 + use_count/last_used.

---

## 8. 핫키 서비스 (필수 동작)

**`Win32HotkeyService`:**

- `RegisterHotKey` on Qt widget HWND
- `QAbstractNativeEventFilter` for `WM_HOTKEY`
- `set_suppressed(bool)` — 설정 창에서 팝업 방지
- `probe_available(hotkey)`:
  - 현재 등록 키와 `hotkeys_equal` → True
  - else unregister → RegisterHotKey test → UnregisterHotKey → re-register

**`HotkeyCaptureEdit`:**

- `focusInEvent`: Mouse/Tab/Backtab/Shortcut만 `_begin_capture`
- `focusOutEvent`: `_finalize_on_blur` — unchanged → restore; probe 실패 → QMessageBox + restore
- `hotkeys_equal` from `hotkey_parser.normalize_hotkey_string`

---

## 9. PopupWindow (필수 UX)

- Flags: Tool | Frameless | StaysOnTop (`popup_flags.py`)
- QSS: `resources/styles/popup.qss`
- `close_popup_after_paste` callable — **기본 lambda False** from controller
- Paste: 30ms timer → `PasteService.paste_snippet` → success 시 조건부 close
- Flyouts: `SnippetDetailFlyout`, `SnippetFlyout` + hover_zone leave logic
- Bottom buttons: hide popup → open manager or settings

---

## 10. PasteService

- Text: win_clipboard Unicode+mbcs, SendInput Ctrl+V, optional clipboard restore
- Image: paste_target block check, set image path to clipboard, Ctrl+V
- Record `usage_events` with error codes

---

## 11. SettingsWindow UI

단일 `QScrollArea` + sections:

1. 호출·트리거 — HotkeyCaptureEdit + status labels  
2. 붙여넣기 — toggles + paste_delay spin  
3. 팝업 — popup_offset spin only (no width/height UI)  
4. 데이터·백업 — backup interval + hint for tray export/import  

`showEvent`: focus `_startup` not hotkey field.

---

## 12. Import/Export ZIP

`MANIFEST_VERSION = 1` — export categories, snippets, assets, optional settings keys listed in `import_export_package.py`.

Tray: QFileDialog save/open → `ImportExportService`.

---

## 13. Backup

`BackupScheduler` QTimer — copy db+settings to `backups/backup_YYYYMMDD_*`, prune by keep count.

---

## 14. Help

`HelpWindow` + `build_help_html` — inject configured + active hotkey + `DEFAULT_HOTKEY` text.

---

## 15. 구현하지 말 것 (v3)

| 항목 | 이유 |
|------|------|
| 마우스 휠/가운데 버튼 트리거 UI | 제거됨; `mouse_trigger_service` 연결 안 함 |
| 테마/글자 크기 설정 | 제거됨 |
| Shell Extension | 비목표 |
| `image_paste_mode` UI | 키만 존재, 미사용 |

---

## 16. 테스트 최소 세트

구현 후 반드시 통과:

- `test_config.py` — hotkey default Q, no theme key  
- `test_hotkey_parser.py` — parse, hotkeys_equal  
- `test_popup_close_after_paste.py`, `test_popup_focus_persist.py`  
- `test_import_export.py`  
- `test_help.py`  

목표: `pytest tests/` 70+ passed.

---

## 17. 구현 순서 (권장)

1. paths, config, db, repositories  
2. models + category/snippet CRUD tests  
3. Tray + AppController skeleton  
4. ManagerWindow  
5. Clipboard + Paste + injection  
6. Popup + flyouts + QSS  
7. Hotkey service + parser + capture edit  
8. Settings + startup + backup + import/export  
9. Help, single instance, icons  
10. PyInstaller spec + installer scripts  

---

## 18. 문서 맵

| 질문 | 문서 |
|------|------|
| 왜 만드나 | 기획서_v3.md |
| 무엇을 만드나 | prd_v3.md |
| 화면별 동작 | 기능명세서_v3.md |
| 레이어·흐름 | architecture.md |
| 배포 | deploy.md |

---

## 19. 검증 체크리스트 (수동)

- [ ] 트레이 상주, 단축키 `Ctrl+Shift+Q` 팝업  
- [ ] 설정 열 때 단축키 필드에 값 표시, 클릭 후에만 입력  
- [ ] 동일 단축키 재입력 시 오류 없음  
- [ ] 붙여넣기 후 팝업 기본 유지  
- [ ] ZIP export/import  
- [ ] 두 번째 실행 시 안내  
- [ ] 도움말에 단축키 표시  

---

*본 문서는 `doc/04. quickpaste_manager_cursor_kickoff_v3.md`와 동일 목적이다.*
