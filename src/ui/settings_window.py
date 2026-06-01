"""환경설정 창 뼈대."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.utils.config import default_settings


class SettingsWindow(QMainWindow):
    def __init__(
        self,
        settings: dict,
        *,
        on_save: Callable[[dict], None] | None = None,
    ) -> None:
        super().__init__()
        self._settings = dict(settings)
        self._on_save = on_save

        self.setWindowTitle("QuickPaste Manager — 환경설정")
        self.resize(520, 420)
        self._build_ui()
        self.load_settings(self._settings)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        tabs = QTabWidget()

        # 일반
        general = QWidget()
        general_form = QFormLayout(general)
        self._theme_edit = QLineEdit()
        self._font_size = QSpinBox()
        self._font_size.setRange(8, 24)
        general_form.addRow("테마", self._theme_edit)
        general_form.addRow("글자 크기", self._font_size)
        tabs.addTab(general, "일반")

        # 호출 방식
        trigger = QWidget()
        trigger_form = QFormLayout(trigger)
        self._hotkey_edit = QLineEdit()
        self._hotkey_status = QLabel("")
        self._hotkey_status.setWordWrap(True)
        self._hotkey_status.setStyleSheet("color: #666;")
        self._mouse_wheel = QCheckBox("마우스 가운데 버튼(휠 클릭)으로 팝업 호출")
        self._startup = QCheckBox("Windows 시작 시 실행")
        self._startup_status = QLabel("")
        self._startup_status.setWordWrap(True)
        self._startup_status.setStyleSheet("color: #666;")
        trigger_form.addRow("호출 단축키", self._hotkey_edit)
        trigger_form.addRow("등록 상태", self._hotkey_status)
        trigger_form.addRow("", self._mouse_wheel)
        trigger_form.addRow("", self._startup)
        trigger_form.addRow("", self._startup_status)
        tabs.addTab(trigger, "호출 방식")

        # 붙여넣기
        paste = QWidget()
        paste_form = QFormLayout(paste)
        self._paste_delay = QSpinBox()
        self._paste_delay.setRange(0, 2000)
        self._paste_delay.setSuffix(" ms")
        self._restore_clipboard = QCheckBox("붙여넣기 후 클립보드 복원")
        paste_form.addRow("자동 붙여넣기 지연", self._paste_delay)
        paste_form.addRow("", self._restore_clipboard)
        tabs.addTab(paste, "붙여넣기")

        # 데이터
        data = QWidget()
        data_form = QFormLayout(data)
        self._backup_interval = QSpinBox()
        self._backup_interval.setRange(1, 168)
        self._backup_interval.setSuffix(" 시간")
        data_form.addRow("자동 백업 주기", self._backup_interval)
        data_form.addRow(QLabel("내보내기/불러오기는 트레이 메뉴에서 사용"))
        tabs.addTab(data, "데이터")

        # 고급
        advanced = QWidget()
        advanced_form = QFormLayout(advanced)
        self._popup_offset = QSpinBox()
        self._popup_offset.setRange(0, 100)
        self._popup_offset.setSuffix(" px")
        advanced_form.addRow("팝업 위치 보정", self._popup_offset)
        advanced_form.addRow(QLabel("TODO: 이미지 붙여넣기 방식, 고급 옵션"))
        tabs.addTab(advanced, "고급")

        layout.addWidget(tabs)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def load_settings(
        self,
        settings: dict,
        *,
        hotkey_active: str | None = None,
        startup_active: bool | None = None,
    ) -> None:
        self._settings = dict(settings)
        self._theme_edit.setText(str(settings.get("theme", "system")))
        self._font_size.setValue(int(settings.get("font_size", 10)))
        configured = str(settings.get("hotkey", "Ctrl+Shift+V"))
        self._hotkey_edit.setText(configured)
        if hotkey_active:
            self._hotkey_status.setText(
                f"✅ 시스템에 등록됨: {hotkey_active}"
            )
            if hotkey_active != configured:
                self._hotkey_status.setText(
                    f"⚠ 저장값({configured})과 다름 — 실제 등록: {hotkey_active}"
                )
        else:
            self._hotkey_status.setText(
                "❌ 전역 단축키 미등록 — 다른 앱 충돌 또는 이전 프로세스 잔존 가능"
            )
        self._mouse_wheel.setChecked(bool(settings.get("mouse_wheel_trigger_enabled", False)))
        wants_startup = bool(settings.get("startup_with_windows", False))
        self._startup.setChecked(wants_startup)
        if startup_active is None:
            self._startup_status.setText("")
        elif startup_active:
            self._startup_status.setText("✅ 시작 프로그램에 등록되어 있습니다.")
            if not wants_startup:
                self._startup_status.setText(
                    "⚠ 시작 프로그램에는 등록되어 있으나 설정은 꺼져 있습니다. "
                    "저장하면 해제됩니다."
                )
        else:
            self._startup_status.setText("시작 프로그램 미등록")
            if wants_startup:
                self._startup_status.setText(
                    "⚠ 설정은 켜져 있으나 아직 등록되지 않았습니다. 저장하면 등록됩니다."
                )
        self._paste_delay.setValue(int(settings.get("paste_delay_ms", 50)))
        self._restore_clipboard.setChecked(bool(settings.get("restore_clipboard_after_paste", True)))
        self._backup_interval.setValue(int(settings.get("auto_backup_interval_hours", 24)))
        self._popup_offset.setValue(int(settings.get("popup_offset_px", 12)))

    def _save(self) -> None:
        updated = default_settings()
        updated.update(self._settings)
        updated.update({
            "theme": self._theme_edit.text().strip() or "system",
            "font_size": self._font_size.value(),
            "hotkey": self._hotkey_edit.text().strip() or "Ctrl+Shift+V",
            "mouse_wheel_trigger_enabled": self._mouse_wheel.isChecked(),
            "startup_with_windows": self._startup.isChecked(),
            "paste_delay_ms": self._paste_delay.value(),
            "restore_clipboard_after_paste": self._restore_clipboard.isChecked(),
            "auto_backup_interval_hours": self._backup_interval.value(),
            "popup_offset_px": self._popup_offset.value(),
        })
        self._settings = updated
        if self._on_save:
            self._on_save(updated)
        self.close()
