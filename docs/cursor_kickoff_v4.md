# Cursor 개발 착수본 v4 — QuickPaste Manager

> **목적:** v4 문서·현행 `main` 브랜치와 **동일한** Windows 상용구 유틸리티를 구현·유지한다.  
> 화면 규칙: [기능명세서_v4.md](./기능명세서_v4.md) · 요구사항: [prd_v4.md](./prd_v4.md)

| 항목 | 값 |
|------|-----|
| 문서 버전 | 4.0 |
| 작성일 | 2026-05-31 |
| 앱 버전 | 0.2.3 |
| Python | 3.12+ |
| OS | Windows 10/11 x64 |

---

## 1. Cursor 역할

1. v4 **Must** 구현·유지 (v3 Must + FR-21~27).
2. `pytest` **83+** 통과.
3. Won't: 마우스 휠 UI, 테마, Shell Extension.

---

## 2. 실행

```powershell
cd "D:\Smit_Dev\Python\QuickPaste Manager"
.\scripts\bootstrap.ps1
.\scripts\dev_run.ps1
python -m pytest tests/ -q
```

---

## 3. v4 필수 UX (PopupWindow + Flyouts)

### 3.1 `close_popup_after_paste`

- Controller: `lambda: settings["close_popup_after_paste"]` (기본 **False**)
- 성공 시 **false** → flyout·detail **hide 하지 않음**

### 3.2 HWND (`popup_window.py`)

```python
# show_near_cursor
self._target_hwnd = capture_foreground_window()

# persist mode only
_target_poll_timer 100ms → _sync_external_target_hwnd()
# outside our UI → capture_window_at_cursor()
# else → capture_foreground_window(), exclude _popup_hwnds()
```

`capture_window_at_cursor`: `input_injection.py` — `WindowFromPoint` + `GetAncestor(GA_ROOT)`.

### 3.3 `SnippetFlyout`

- 목록만; hover → `_ensure_detail()` → `SnippetDetailFlyout.show_snippet` at list.right+4
- **No** `leaveEvent` auto-close
- Close: header × → `on_close` → `_hide_category_flyout`

### 3.4 `SnippetFlyout` + Top 5

- 카테고리 목록 열림 + Top 5 hover → `_top_detail_anchor()` → flyout.right+4
- `flyout.reset_detail_panel()` before Top 5 detail
- Top 5 detail: leave Top 5 zone only to close (not on paste)

---

## 4. 클립보드 (`win_clipboard.py`)

```python
def exclude_from_clipboard_history() -> bool:
    ctypes.windll.user32.ExcludeClipboardContentFromMonitorProcessing()
```

Call **before** `OpenClipboard` / `setImage`.

---

## 5. 설정 기본값 (`config.py`)

```python
DEFAULT_HOTKEY = "Ctrl+Shift+Q"
DEFAULT_SETTINGS = {
    "close_popup_after_paste": False,
    "restore_clipboard_after_paste": True,
    ...
}
```

---

## 6. 테스트 필수 (v4)

- `test_popup_close_after_paste.py` — persist, flyout on leave, category flyout after paste
- `test_popup_focus_persist.py` — sync HWND, deactivate
- `test_clipboard_history_exclude.py`
- `test_input_injection.py` — `capture_window_at_cursor`

---

## 7. 구현하지 말 것

v3와 동일: 마우스 휠 UI, 테마, `image_paste_mode` UI.

---

## 8. 문서 맵

| 질문 | 문서 |
|------|------|
| 왜 | 기획서_v4.md |
| 무엇 | prd_v4.md |
| 화면 | 기능명세서_v4.md |
| 레이어 | architecture.md |
| 배포 | deploy.md |

---

## 9. 수동 검증 체크리스트

- [ ] 카테고리 클릭 → 목록 → 오버 시 **목록 우측** 상세
- [ ] 마우스를 Word로 옮겨 붙여넣기 → **목록 창 유지**
- [ ] a창 붙여넣기 → b창 클릭 → b에 붙여넣기 (유지 모드)
- [ ] Win+V에 상용구 텍스트가 쌓이지 않음(Win10 1809+)
- [ ] 카테고리 열림 상태에서 Top 5 오버 → 목록 **우측** Top 5 상세
- [ ] Top 5 붙여넣기 후 상세는 리스트 이탈 시에만 닫힘

---

*v3 착수본: [cursor_kickoff_v3.md](./cursor_kickoff_v3.md) · `doc/05. quickpaste_manager_cursor_kickoff_v4.md`*
