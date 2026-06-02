# QuickPaste Manager — 아키텍처 (v4)

| 항목 | 내용 |
|------|------|
| 문서 버전 | 4.0 |
| 작성일 | 2026-05-31 |

---

## 1. 레이어 구조

```text
┌─────────────────────────────────────────────────────────┐
│  Presentation (PySide6)                                  │
│  PopupWindow, ManagerWindow, SettingsWindow, HelpWindow │
│  TrayController, widgets (flyout, hotkey capture, …)      │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Application                                             │
│  AppController — 오케스트레이션, 설정, 창 생명주기        │
│  BackupScheduler, SingleInstanceGuard (main)             │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Domain Services                                         │
│  Hotkey, Paste, Clipboard, ImportExport, Backup, Asset   │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Data Access                                             │
│  Repositories → SQLite (app.db)                          │
│  Filesystem: assets/, settings.json, backups/          │
└─────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│  Platform (Windows)                                        │
│  RegisterHotKey, SendInput, Win32 clipboard, startup reg │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 프로세스·스레드

| 항목 | 정책 |
|------|------|
| 메인 스레드 | Qt GUI + native event filter (hotkey) |
| DB | 단일 `sqlite3.Connection` per AppController, WAL 미사용(단순 연결) |
| 백업 타이머 | `QTimer` in BackupScheduler |
| 붙여넣기 | UI thread에서 30ms deferred paste |

---

## 3. 데이터 흐름 — 붙여넣기

```text
[Hotkey / Tray] → AppController.open_popup()
    → PopupWindow.show_near_cursor()
    → capture_foreground_window()  → _target_hwnd

[Persist mode] QTimer 100ms → _sync_external_target_hwnd()
    → cursor outside our HWNDs → capture_window_at_cursor()
    → else → capture_foreground_window() (exclude popup/flyout/detail)

User clicks snippet
    → _sync_external_target_hwnd()
    → PasteService.paste_snippet(conn, snippet, target_hwnd)
        → exclude_from_clipboard_history()
        → ClipboardService / win_clipboard (set content)
        → QTimer(paste_delay_ms)
        → input_injection.send_ctrl_v + restore foreground
        → usage_repository.insert
    → if success && close_popup_after_paste: close all popups
    → else: keep main + category list + detail, topmost refresh
```

---

## 4. 데이터 흐름 — 설정·핫키

```text
SettingsWindow.save
    → save_settings(json)
    → AppController._reregister_triggers()
        → hotkey_service.unregister()
        → register(new_hotkey, open_popup)

Settings open:
    → set_suppressed(True)
Settings close:
    → set_suppressed(False)

HotkeyCaptureEdit blur:
    → hotkey_service.probe_available(candidate)
```

---

## 5. 데이터 흐름 — Import/Export

```text
Export: DB read → ZIP(manifest, categories, snippets, assets/, settings subset)
Import: ZIP parse → merge categories/snippets → copy assets → optional settings merge
```

---

## 6. AppData 레이아웃

```text
%APPDATA%\QuickPasteManager\
├─ app.db
├─ settings.json
├─ assets\
├─ logs\
├─ backups\backup_YYYYMMDD_HHMMSS\
└─ exports\   (보내기 대화상자 기본 경로)
```

소스·설치 경로와 분리 → 업데이트·재설치 시 데이터 유지.

---

## 7. 단일 인스턴스

```text
QLocalServer "QuickPasteManager"
  ├─ primary: listen + AppController
  └─ secondary: send "activate" → primary opens popup → exit
```

---

## 8. 모듈 의존 규칙

| 허용 | 금지 |
|------|------|
| ui → services, repositories, models, utils | repositories → ui |
| app → ui, services, repositories | services → ui (PasteService는 QMessageBox 최소) |
| services → repositories, utils | |

---

## 9. 보조 창 구조 (v4)

```text
[Main Popup]──+── SnippetDetailFlyout (Top5 hover)
              │
              └── SnippetFlyout (category list)
                        └── SnippetDetailFlyout (category hover)
```

카테고리 목록은 마우스 이탈로 닫히지 않음(× 또는 메인 닫기 등). 상세만 list+detail 영역 이탈 시 reset.

---

## 10. Phase 상태 (v4)

| Phase | 내용 | 상태 |
|-------|------|------|
| 1–6 | v3 Phase 1–6 | ✅ |
| 7 | 팝업 유지·다중 HWND·Win+V 제외 | ✅ |
| 8 | 카테고리 우측 상세·목록 × 닫기 | ✅ |
| 9 | 마우스 트리거 연동 | ⬜ 보류 |
| 10 | 코드 서명 | ⬜ deploy.md |

---

## 11. 관련 문서

- [기능명세서_v4.md](./기능명세서_v4.md)
- [cursor_kickoff_v4.md](./cursor_kickoff_v4.md)
- [deploy.md](./deploy.md)
