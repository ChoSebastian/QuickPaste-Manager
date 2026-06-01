"""Windows 시작 프로그램(HKCU Run) 등록."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger("quickpaste.startup")

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_VALUE_NAME = "QuickPasteManager"


def get_launch_command() -> str:
    """시작 시 실행할 명령줄 (따옴표 포함)."""
    exe = Path(sys.executable)
    if getattr(sys, "frozen", False):
        return f'"{exe}"'
    project_root = Path(__file__).resolve().parents[2]
    return f'"{exe}" -m src.main'


def is_startup_enabled() -> bool:
    if sys.platform != "win32":
        return False
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_READ
        ) as key:
            winreg.QueryValueEx(key, _VALUE_NAME)
        return True
    except FileNotFoundError:
        return False
    except OSError as exc:
        logger.warning("시작 프로그램 조회 실패: %s", exc)
        return False


def apply_startup_setting(enabled: bool) -> tuple[bool, str]:
    """시작 프로그램 등록/해제. (성공 여부, 사용자 메시지)"""
    if sys.platform != "win32":
        return True, ""

    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            _RUN_KEY,
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_READ,
        ) as key:
            if enabled:
                command = get_launch_command()
                winreg.SetValueEx(key, _VALUE_NAME, 0, winreg.REG_SZ, command)
                logger.info("시작 프로그램 등록: %s", command)
                return True, "Windows 시작 시 자동 실행이 등록되었습니다."
            try:
                winreg.DeleteValue(key, _VALUE_NAME)
                logger.info("시작 프로그램 등록 해제")
                return True, "Windows 시작 시 자동 실행이 해제되었습니다."
            except FileNotFoundError:
                return True, ""
    except OSError as exc:
        logger.exception("시작 프로그램 설정 실패")
        return False, f"시작 프로그램 설정에 실패했습니다.\n\n{exc}"
