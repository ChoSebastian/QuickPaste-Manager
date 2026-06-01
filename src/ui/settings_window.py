"""환경설정 — 단일 스크롤 화면 (ON/OFF + 입력)."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.ui.widgets.hotkey_capture_edit import HotkeyCaptureEdit
from src.ui.widgets.settings_controls import (
    SettingDivider,
    SettingSectionTitle,
    SettingSpinRow,
    SettingToggle,
)
from src.utils.config import DEFAULT_HOTKEY, default_settings
from src.utils.hotkey_parser import is_valid_hotkey_string
from src.utils.hotkey_probe import probe_hotkey_available


class SettingsWindow(QMainWindow):
    def __init__(
        self,
        settings: dict,
        *,
        on_save: Callable[[dict], None] | None = None,
        hotkey_probe_fn: Callable[[str], tuple[bool, str]] | None = None,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self._settings = dict(settings)
        self._on_save = on_save
        self._hotkey_probe_fn = hotkey_probe_fn or probe_hotkey_available
        self._on_close = on_close

        self.setWindowTitle("QuickPaste Manager — 환경설정")
        self.resize(480, 580)
        self._build_ui()
        self.load_settings(self._settings)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._startup.setFocus(Qt.FocusReason.OtherFocusReason)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._on_close:
            self._on_close()
        super().closeEvent(event)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(4, 0, 8, 0)
        layout.setSpacing(0)

        layout.addWidget(SettingSectionTitle("호출 · 트리거"))
        hotkey_box = QWidget()
        hotkey_form = QFormLayout(hotkey_box)
        hotkey_form.setContentsMargins(0, 0, 0, 0)
        self._hotkey_edit = HotkeyCaptureEdit(probe_fn=self._hotkey_probe_fn)
        self._hotkey_hint = QLabel(
            "입력란을 클릭한 뒤 Ctrl·Shift 등과 문자 키를 순서대로 누르세요. "
            "Del/Backspace로 지웁니다."
        )
        self._hotkey_hint.setWordWrap(True)
        self._hotkey_hint.setStyleSheet("color: #888; font-size: 11px;")
        self._hotkey_status = QLabel("")
        self._hotkey_status.setWordWrap(True)
        self._hotkey_status.setStyleSheet("color: #666; font-size: 11px;")
        hotkey_form.addRow("단축키", self._hotkey_edit)
        hotkey_form.addRow("", self._hotkey_hint)
        hotkey_form.addRow("", self._hotkey_status)
        layout.addWidget(hotkey_box)

        self._startup = SettingToggle(
            "Windows 시작 시 실행",
            hint="로그인 시 트레이에서 자동 실행됩니다.",
        )
        layout.addWidget(self._startup)
        self._startup_status = QLabel("")
        self._startup_status.setWordWrap(True)
        self._startup_status.setStyleSheet("color: #666; font-size: 11px; padding-left: 2px;")
        layout.addWidget(self._startup_status)

        layout.addWidget(SettingDivider())

        layout.addWidget(SettingSectionTitle("붙여넣기"))
        self._close_after_paste = SettingToggle(
            "붙여넣기 후 팝업 닫기",
            hint="끄면 팝업을 유지한 채 여러 곳에 연속 붙여넣기할 수 있습니다.",
        )
        layout.addWidget(self._close_after_paste)
        self._restore_clipboard = SettingToggle(
            "붙여넣기 후 클립보드 복원",
            hint="붙여넣기 전 클립보드 내용을 되돌립니다.",
        )
        layout.addWidget(self._restore_clipboard)
        self._paste_delay = SettingSpinRow(
            "자동 붙여넣기 지연",
            suffix=" ms",
            minimum=0,
            maximum=2000,
        )
        layout.addWidget(self._paste_delay)

        layout.addWidget(SettingDivider())

        layout.addWidget(SettingSectionTitle("팝업"))
        self._popup_offset = SettingSpinRow(
            "커서 위치 보정",
            suffix=" px",
            minimum=0,
            maximum=100,
        )
        layout.addWidget(self._popup_offset)

        layout.addWidget(SettingDivider())

        layout.addWidget(SettingSectionTitle("데이터 · 백업"))
        self._backup_interval = SettingSpinRow(
            "자동 백업 주기",
            suffix=" 시간",
            minimum=1,
            maximum=168,
        )
        layout.addWidget(self._backup_interval)
        data_hint = QLabel("보내기 / 불러오기는 트레이 메뉴에서 사용합니다.")
        data_hint.setStyleSheet("color: #888; font-size: 11px; padding: 4px 0 8px 0;")
        data_hint.setWordWrap(True)
        layout.addWidget(data_hint)

        layout.addStretch()
        scroll.setWidget(body)
        root.addWidget(scroll)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("저장")
        save_btn.setMinimumWidth(88)
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        root.addLayout(btn_row)

    def load_settings(
        self,
        settings: dict,
        *,
        hotkey_active: str | None = None,
        startup_active: bool | None = None,
    ) -> None:
        self._settings = dict(settings)
        configured = str(settings.get("hotkey", DEFAULT_HOTKEY))
        self._hotkey_edit.setHotkey(configured)

        if hotkey_active:
            self._hotkey_status.setText(f"✅ 현재 등록됨: {hotkey_active}")
            if hotkey_active != configured:
                self._hotkey_status.setText(
                    f"⚠ 저장값({configured})과 다름 — 실제 등록: {hotkey_active}"
                )
        else:
            self._hotkey_status.setText(
                "❌ 전역 단축키 미등록 — 포커스를 벗어날 때 등록 가능 여부를 확인합니다."
            )

        self._startup.setChecked(bool(settings.get("startup_with_windows", True)))
        wants_startup = self._startup.isChecked()

        if startup_active is None:
            self._startup_status.setText("")
        elif startup_active:
            self._startup_status.setText("✅ 시작 프로그램에 등록되어 있습니다.")
            if not wants_startup:
                self._startup_status.setText(
                    "⚠ 시작 프로그램에는 등록되어 있으나 설정은 꺼져 있습니다."
                )
        else:
            self._startup_status.setText("시작 프로그램 미등록")
            if wants_startup:
                self._startup_status.setText(
                    "⚠ 설정은 켜져 있으나 아직 등록되지 않았습니다. 저장 시 등록됩니다."
                )

        self._close_after_paste.setChecked(
            bool(settings.get("close_popup_after_paste", False))
        )
        self._paste_delay.setValue(int(settings.get("paste_delay_ms", 50)))
        self._restore_clipboard.setChecked(
            bool(settings.get("restore_clipboard_after_paste", True))
        )
        self._backup_interval.setValue(
            int(settings.get("auto_backup_interval_hours", 24))
        )
        self._popup_offset.setValue(int(settings.get("popup_offset_px", 12)))

    def _save(self) -> None:
        hotkey = self._hotkey_edit.hotkey().strip() or DEFAULT_HOTKEY
        if not is_valid_hotkey_string(hotkey):
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self,
                "단축키",
                "올바른 단축키를 입력해 주세요.\n예: Ctrl+Shift+Q",
            )
            self._hotkey_edit.setFocus()
            return

        ok, message = self._hotkey_probe_fn(hotkey)
        if not ok:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self,
                "단축키 사용 불가",
                message + "\n\n다른 조합을 입력해 주세요.",
            )
            self._hotkey_edit.setFocus()
            return

        updated = default_settings()
        updated.update(self._settings)
        updated.update(
            {
                "hotkey": hotkey,
                "startup_with_windows": self._startup.isChecked(),
                "close_popup_after_paste": self._close_after_paste.isChecked(),
                "paste_delay_ms": self._paste_delay.value(),
                "restore_clipboard_after_paste": self._restore_clipboard.isChecked(),
                "auto_backup_interval_hours": self._backup_interval.value(),
                "popup_offset_px": self._popup_offset.value(),
            }
        )
        self._settings = updated
        if self._on_save:
            self._on_save(updated)
        self.close()
