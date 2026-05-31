"""Windows 호환 유틸리티."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def open_folder_in_explorer(folder_path: Path) -> None:
    """Windows 탐색기에서 폴더를 연다."""
    path = str(folder_path.resolve())
    if sys.platform == "win32":
        os.startfile(path)  # noqa: S606
    else:
        subprocess.run(["xdg-open", path], check=False)


def show_user_warning(title: str, message: str) -> None:
    """간단한 사용자 경고 메시지를 표시한다."""
    try:
        from PySide6.QtWidgets import QMessageBox

        box = QMessageBox()
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(title)
        box.setText(message)
        box.exec()
    except Exception:
        print(f"[WARNING] {title}: {message}", file=sys.stderr)
