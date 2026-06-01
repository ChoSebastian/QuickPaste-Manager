"""붙여넣기 서비스."""

from __future__ import annotations

import logging
import sqlite3
import time
from pathlib import Path
from typing import Protocol

from src.models.snippet import Snippet
from src.repositories import asset_repository, snippet_repository, usage_repository
from src.services.clipboard_service import ClipboardService
from src.utils.input_injection import send_ctrl_v
from src.utils.paste_target import image_paste_blocked_reason
from src.utils.win_compat import open_folder_in_explorer, show_user_warning

logger = logging.getLogger("quickpaste.paste")

FOCUS_DELAY_MS = 80
CLIPBOARD_SETTLE_MS = 80
RESTORE_CLIPBOARD_DELAY_MS = 150


class PasteService(Protocol):
    def paste_snippet(
        self,
        conn: sqlite3.Connection,
        snippet: Snippet,
        *,
        target_hwnd: int | None = None,
        show_warning: bool = True,
    ) -> bool: ...
    def set_paste_delay_ms(self, delay_ms: int) -> None: ...
    def set_restore_clipboard(self, enabled: bool) -> None: ...
    def show_pending_warning(self) -> None: ...


class DefaultPasteService:

    def __init__(
        self,
        clipboard: ClipboardService,
        *,
        paste_delay_ms: int = 50,
        restore_clipboard: bool = True,
    ) -> None:
        self._clipboard = clipboard
        self._paste_delay_ms = paste_delay_ms
        self._restore_clipboard = restore_clipboard
        self._pending_warning: tuple[str, str] | None = None

    def show_pending_warning(self) -> None:
        """붙여넣기 실패 메시지를 팝업 닫힌 뒤 표시한다."""
        if self._pending_warning is None:
            return
        title, message = self._pending_warning
        self._pending_warning = None
        show_user_warning(title, message)

    def _fail(
        self,
        title: str,
        message: str,
        *,
        show_warning: bool,
    ) -> bool:
        self._pending_warning = (title, message)
        if show_warning:
            show_user_warning(title, message)
            self._pending_warning = None
        return False

    def set_paste_delay_ms(self, delay_ms: int) -> None:
        self._paste_delay_ms = delay_ms

    def set_restore_clipboard(self, enabled: bool) -> None:
        self._restore_clipboard = enabled

    def paste_snippet(
        self,
        conn: sqlite3.Connection,
        snippet: Snippet,
        *,
        target_hwnd: int | None = None,
        show_warning: bool = True,
    ) -> bool:
        if snippet.content_type == "text":
            return self._paste_text(
                conn, snippet, target_hwnd=target_hwnd, show_warning=show_warning
            )
        if snippet.content_type == "image":
            return self._paste_image(
                conn, snippet, target_hwnd=target_hwnd, show_warning=show_warning
            )
        logger.warning("지원하지 않는 content_type: %s", snippet.content_type)
        return False

    def _paste_text(
        self,
        conn: sqlite3.Connection,
        snippet: Snippet,
        *,
        target_hwnd: int | None,
        show_warning: bool,
    ) -> bool:
        body = snippet.body_text or ""
        previous = self._clipboard.get_text() if self._restore_clipboard else ""

        if not self._clipboard.set_text(body):
            self._record_failure(conn, snippet.id, "CLIPBOARD_TEXT_FAILED")
            return self._fail(
                "붙여넣기 실패", "클립보드 등록에 실패했습니다.", show_warning=show_warning
            )

        time.sleep(CLIPBOARD_SETTLE_MS / 1000.0)
        time.sleep(self._paste_delay_ms / 1000.0)

        if not send_ctrl_v(target_hwnd=target_hwnd, focus_delay_ms=FOCUS_DELAY_MS):
            self._record_failure(conn, snippet.id, "SENDINPUT_FAILED")
            return self._fail(
                "붙여넣기 실패",
                "자동 붙여넣기에 실패했습니다. 클립보드에 복사되었으니 Ctrl+V를 눌러주세요.",
                show_warning=show_warning,
            )

        if self._restore_clipboard and previous:
            time.sleep(RESTORE_CLIPBOARD_DELAY_MS / 1000.0)
            self._clipboard.set_text(previous)

        self._record_success(conn, snippet.id)
        logger.info("텍스트 붙여넣기 완료: snippet_id=%d", snippet.id)
        return True

    def _paste_image(
        self,
        conn: sqlite3.Connection,
        snippet: Snippet,
        *,
        target_hwnd: int | None,
        show_warning: bool,
    ) -> bool:
        blocked = image_paste_blocked_reason(target_hwnd)
        if blocked is not None:
            self._record_failure(conn, snippet.id, "IMAGE_TARGET_UNSUPPORTED")
            return self._fail("이미지 붙여넣기", blocked, show_warning=show_warning)

        if snippet.asset_id is None:
            self._record_failure(conn, snippet.id, "IMAGE_ASSET_MISSING")
            return self._fail(
                "이미지 붙여넣기", "연결된 이미지가 없습니다.", show_warning=show_warning
            )

        asset = asset_repository.get_by_id(conn, snippet.asset_id)
        if asset is None:
            self._record_failure(conn, snippet.id, "IMAGE_ASSET_NOT_FOUND")
            return self._fail(
                "이미지 붙여넣기",
                "이미지 파일 정보를 찾을 수 없습니다.",
                show_warning=show_warning,
            )

        image_path = Path(asset.stored_path)
        if not image_path.exists():
            self._record_failure(conn, snippet.id, "IMAGE_FILE_MISSING")
            if show_warning:
                self._handle_image_failure(image_path.parent)
            else:
                self._pending_warning = (
                    "이미지 붙여넣기 실패",
                    "이미지 붙여넣기에 실패했습니다. 파일 위치를 엽니다.",
                )
            return False

        if not self._clipboard.set_image_from_path(image_path):
            self._record_failure(conn, snippet.id, "CLIPBOARD_IMAGE_FAILED")
            if show_warning:
                self._handle_image_failure(image_path.parent)
            else:
                self._pending_warning = (
                    "이미지 붙여넣기 실패",
                    "이미지 붙여넣기에 실패했습니다. 파일 위치를 엽니다.",
                )
            return False

        time.sleep(self._paste_delay_ms / 1000.0)

        if not send_ctrl_v(target_hwnd=target_hwnd, focus_delay_ms=FOCUS_DELAY_MS):
            self._record_failure(conn, snippet.id, "SENDINPUT_IMAGE_FAILED")
            return self._fail(
                "이미지 붙여넣기 실패",
                "이 곳에는 이미지를 붙여넣을 수 없거나 자동 붙여넣기에 실패했습니다.\n"
                "이미지를 지원하는 프로그램(그림판, Word 등)에서 다시 시도해 주세요.",
                show_warning=show_warning,
            )

        self._record_success(conn, snippet.id)
        logger.info("이미지 붙여넣기 완료: snippet_id=%d", snippet.id)
        return True

    def _handle_image_failure(self, folder: Path) -> None:
        show_user_warning(
            "이미지 붙여넣기 실패",
            "이미지 붙여넣기에 실패했습니다. 파일 위치를 엽니다.",
        )
        open_folder_in_explorer(folder)

    def _record_success(self, conn: sqlite3.Connection, snippet_id: int) -> None:
        snippet_repository.record_usage(conn, snippet_id)
        usage_repository.record(conn, snippet_id=snippet_id, success=True)
        conn.commit()

    def _record_failure(
        self,
        conn: sqlite3.Connection,
        snippet_id: int,
        error_code: str,
    ) -> None:
        usage_repository.record(
            conn,
            snippet_id=snippet_id,
            success=False,
            error_code=error_code,
        )
        conn.commit()


def create_paste_service(
    clipboard: ClipboardService,
    *,
    paste_delay_ms: int = 50,
    restore_clipboard: bool = True,
) -> PasteService:
    return DefaultPasteService(
        clipboard,
        paste_delay_ms=paste_delay_ms,
        restore_clipboard=restore_clipboard,
    )
