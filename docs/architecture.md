# QuickPaste Manager — 아키텍처 개요

## 레이어 구조

```text
main.py
  └─ AppController
       ├─ TrayController (시스템 트레이)
       ├─ PopupWindow / ManagerWindow / SettingsWindow
       ├─ Services (hotkey, mouse, clipboard, paste, backup, import/export)
       └─ Repositories → SQLite (app.db)
```

## 데이터 흐름 (붙여넣기)

```text
호출 → PopupWindow → Snippet 선택
  → PasteService → ClipboardService (텍스트/이미지)
  → [TODO] SendInput Ctrl+V
  → UsageEvent 기록
```

## AppData

모든 런타임 데이터는 `%APPDATA%\QuickPasteManager` 에 저장됩니다.  
소스 코드와 분리되어 재설치·업데이트 시 데이터가 유지됩니다.

## Phase별 구현 상태

| Phase | 내용 | 상태 |
|-------|------|------|
| 1 | 프로젝트 기반, 트레이, AppData, 로그, 설정 | ✅ 착수 완료 |
| 2 | CRUD, asset 저장 | 🔶 관리 창 최소 CRUD |
| 3 | 팝업 UI, 붙여넣기 | 🔶 텍스트·이미지 붙여넣기, Top5 점수 |
| 4 | 글로벌 호출 | 🔶 RegisterHotKey 동작 |
| 5 | Import/Export, 백업 | ⬜ TODO |
| 6~7 | 안정화, 배포 | ⬜ 예정 |
