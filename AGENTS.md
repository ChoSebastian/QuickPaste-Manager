# QuickPaste Manager — AI 에이전트 안내

**마감 버전: v0.2.2** (2026-06-01). 신규 기능 개발은 마감 범위 밖입니다.

이 저장소를 수정·재구현할 때는 **v4 문서**를 기준으로 한다.

1. **착수:** [docs/cursor_kickoff_v4.md](docs/cursor_kickoff_v4.md)
2. **요구사항:** [docs/prd_v4.md](docs/prd_v4.md)
3. **화면·동작:** [docs/기능명세서_v4.md](docs/기능명세서_v4.md)
4. **인덱스:** [docs/INDEX.md](docs/INDEX.md)

## 핵심 상수 (코드와 동기화)

- 기본 단축키: `Ctrl+Shift+Q` (`src/utils/config.py` → `DEFAULT_HOTKEY`)
- `close_popup_after_paste`: 기본 `false`
- `startup_with_windows`: 기본 `true`
- 실행: `.\scripts\dev_run.ps1`
- 테스트: `.\.venv\Scripts\python.exe -m pytest tests/`

## 구현하지 않음

마우스 휠/가운데 버튼 트리거 UI, 테마·글자 크기 설정, Shell Extension, 클라우드.
