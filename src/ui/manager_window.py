"""상용구 관리 창."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.repositories import asset_repository, category_repository, snippet_repository
from src.repositories.category_repository import MAX_CATEGORIES
from src.services.asset_service import save_image_file, save_qimage


class ManagerWindow(QMainWindow):
    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__()
        self._conn = conn
        self._selected_category_id: int | None = None
        self._selected_snippet_id: int | None = None
        self._trash_mode = False

        self.setWindowTitle("QuickPaste Manager — 상용구 관리")
        self.resize(960, 640)
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        filter_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("검색 / 필터...")
        self._search.textChanged.connect(self._on_search)
        filter_row.addWidget(self._search, stretch=1)

        self._view_combo = QComboBox()
        self._view_combo.addItems(["활성 상용구", "휴지통"])
        self._view_combo.currentIndexChanged.connect(self._on_view_changed)
        filter_row.addWidget(self._view_combo)
        root.addLayout(filter_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("카테고리"))

        cat_btn_row = QHBoxLayout()
        self._cat_add_btn = QPushButton("추가")
        self._cat_rename_btn = QPushButton("이름변경")
        self._cat_delete_btn = QPushButton("삭제")
        self._cat_add_btn.clicked.connect(self._add_category)
        self._cat_rename_btn.clicked.connect(self._rename_category)
        self._cat_delete_btn.clicked.connect(self._delete_category)
        for btn in (self._cat_add_btn, self._cat_rename_btn, self._cat_delete_btn):
            cat_btn_row.addWidget(btn)
        left_layout.addLayout(cat_btn_row)

        self._category_list = QListWidget()
        self._category_list.currentItemChanged.connect(self._on_category_selected)
        left_layout.addWidget(self._category_list)
        splitter.addWidget(left)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        self._snippet_label = QLabel("상용구 목록")
        center_layout.addWidget(self._snippet_label)
        self._snippet_list = QListWidget()
        self._snippet_list.currentItemChanged.connect(self._on_snippet_selected)
        center_layout.addWidget(self._snippet_list)
        splitter.addWidget(center)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("상세 편집"))
        form = QFormLayout()
        self._category_combo = QComboBox()
        self._title_edit = QLineEdit()
        self._tags_edit = QLineEdit()
        self._pinned_check = QCheckBox("고정")
        self._body_edit = QTextEdit()
        form.addRow("카테고리", self._category_combo)
        form.addRow("제목", self._title_edit)
        form.addRow("태그", self._tags_edit)
        form.addRow("", self._pinned_check)
        form.addRow("본문", self._body_edit)
        right_layout.addLayout(form)
        splitter.addWidget(right)

        splitter.setSizes([220, 320, 420])
        root.addWidget(splitter)

        btn_row = QHBoxLayout()
        self._add_btn = QPushButton("추가")
        self._update_btn = QPushButton("수정")
        self._delete_btn = QPushButton("삭제")
        self._restore_btn = QPushButton("복구")
        self._empty_trash_btn = QPushButton("휴지통 비우기")

        self._add_btn.clicked.connect(self._add_snippet)
        self._update_btn.clicked.connect(self._update_snippet)
        self._delete_btn.clicked.connect(self._delete_snippet)
        self._restore_btn.clicked.connect(self._restore_snippet)
        self._empty_trash_btn.clicked.connect(self._empty_trash)

        for btn in (
            self._add_btn,
            self._update_btn,
            self._delete_btn,
            self._restore_btn,
            self._empty_trash_btn,
        ):
            btn_row.addWidget(btn)
        root.addLayout(btn_row)

        extra_row = QHBoxLayout()
        self._clip_text_btn = QPushButton("클립보드 텍스트")
        self._clip_image_btn = QPushButton("클립보드 이미지")
        self._image_file_btn = QPushButton("이미지 파일")
        self._clip_text_btn.clicked.connect(self._add_from_clipboard_text)
        self._clip_image_btn.clicked.connect(self._add_from_clipboard_image)
        self._image_file_btn.clicked.connect(self._add_image_file)
        for btn in (self._clip_text_btn, self._clip_image_btn, self._image_file_btn):
            extra_row.addWidget(btn)
        root.addLayout(extra_row)

        self._sync_action_state()

    def refresh(self) -> None:
        self._load_category_combo()
        self._load_categories()
        self._reload_snippet_list()

    def _sync_action_state(self) -> None:
        trash = self._trash_mode
        self._cat_add_btn.setEnabled(not trash)
        self._cat_rename_btn.setEnabled(not trash)
        self._cat_delete_btn.setEnabled(not trash)
        self._add_btn.setEnabled(not trash)
        self._update_btn.setEnabled(not trash)
        self._delete_btn.setEnabled(not trash)
        self._restore_btn.setEnabled(trash)
        self._empty_trash_btn.setEnabled(trash)
        self._clip_text_btn.setEnabled(not trash)
        self._clip_image_btn.setEnabled(not trash)
        self._image_file_btn.setEnabled(not trash)
        self._category_combo.setEnabled(not trash)
        self._pinned_check.setEnabled(not trash)
        self._body_edit.setReadOnly(trash)
        self._title_edit.setReadOnly(trash)
        self._tags_edit.setReadOnly(trash)

    def _load_category_combo(self) -> None:
        current_id = self._category_combo.currentData()
        self._category_combo.clear()
        for cat in category_repository.list_active(self._conn):
            self._category_combo.addItem(cat.name, cat.id)
        if current_id is not None:
            idx = self._category_combo.findData(current_id)
            if idx >= 0:
                self._category_combo.setCurrentIndex(idx)

    def _load_categories(self) -> None:
        selected = self._selected_category_id
        self._category_list.clear()
        for cat in category_repository.list_active(self._conn):
            item = QListWidgetItem(cat.name)
            item.setData(Qt.ItemDataRole.UserRole, cat.id)
            self._category_list.addItem(item)
            if selected == cat.id:
                self._category_list.setCurrentItem(item)

        if self._category_list.count() > 0 and self._category_list.currentItem() is None:
            self._category_list.setCurrentRow(0)

    def _reload_snippet_list(self) -> None:
        keyword = self._search.text().strip().lower()
        self._snippet_list.clear()

        if self._trash_mode:
            snippets = snippet_repository.list_trash(
                self._conn,
                category_id=self._selected_category_id,
            )
            if keyword:
                snippets = [
                    s
                    for s in snippets
                    if keyword in s.title.lower()
                    or keyword in s.tags.lower()
                    or (s.body_text and keyword in s.body_text.lower())
                ]
        elif keyword:
            snippets = snippet_repository.search(self._conn, keyword)
        elif self._selected_category_id is not None:
            snippets = snippet_repository.list_by_category(
                self._conn, self._selected_category_id
            )
        else:
            snippets = []

        for snippet in snippets:
            label = self._snippet_label_text(snippet)
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, snippet.id)
            self._snippet_list.addItem(item)

        trash_count = snippet_repository.count_trash(self._conn)
        self._snippet_label.setText(
            f"상용구 목록 ({'휴지통' if self._trash_mode else '활성'})"
        )
        self._empty_trash_btn.setText(f"휴지통 비우기 ({trash_count})")

    def _snippet_label_text(self, snippet) -> str:
        label = snippet.title
        if snippet.content_type == "image":
            label = f"🖼 {label}"
        if self._trash_mode:
            return f"🗑 {label}"
        if snippet.pinned:
            return f"📌 {label}"
        return label

    def _on_view_changed(self, index: int) -> None:
        self._trash_mode = index == 1
        self._sync_action_state()
        self._clear_detail()
        self._reload_snippet_list()

    def _on_category_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            return
        self._selected_category_id = current.data(Qt.ItemDataRole.UserRole)
        self._reload_snippet_list()
        self._clear_detail()

    def _on_snippet_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            return
        snippet_id = current.data(Qt.ItemDataRole.UserRole)
        snippet = snippet_repository.get_by_id(self._conn, snippet_id)
        if snippet is None:
            return
        self._selected_snippet_id = snippet_id
        self._title_edit.setText(snippet.title)
        self._tags_edit.setText(snippet.tags)
        self._pinned_check.setChecked(snippet.pinned)
        if snippet.content_type == "image":
            asset = (
                asset_repository.get_by_id(self._conn, snippet.asset_id)
                if snippet.asset_id
                else None
            )
            path_text = asset.original_name if asset else "(이미지 없음)"
            self._body_edit.setPlainText(f"[이미지] {path_text}")
            self._body_edit.setReadOnly(True)
        else:
            self._body_edit.setPlainText(snippet.body_text or "")
            self._body_edit.setReadOnly(self._trash_mode)
        idx = self._category_combo.findData(snippet.category_id)
        if idx >= 0:
            self._category_combo.setCurrentIndex(idx)

    def _clear_detail(self) -> None:
        self._selected_snippet_id = None
        self._title_edit.clear()
        self._tags_edit.clear()
        self._body_edit.clear()
        self._body_edit.setReadOnly(self._trash_mode)
        self._pinned_check.setChecked(False)

    def _on_search(self, text: str) -> None:
        _ = text
        self._reload_snippet_list()

    def _add_category(self) -> None:
        if category_repository.count_active(self._conn) >= MAX_CATEGORIES:
            QMessageBox.warning(
                self,
                "카테고리",
                f"카테고리는 최대 {MAX_CATEGORIES}개까지 생성할 수 있습니다.",
            )
            return

        name, ok = QInputDialog.getText(self, "카테고리 추가", "이름:")
        if not ok or not name.strip():
            return

        try:
            category_repository.create(
                self._conn,
                name=name.strip(),
                sort_order=category_repository.next_sort_order(self._conn),
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "카테고리", "같은 이름의 카테고리가 이미 있습니다.")
            return

        self.refresh()

    def _rename_category(self) -> None:
        if self._selected_category_id is None:
            QMessageBox.warning(self, "카테고리", "변경할 카테고리를 선택하세요.")
            return

        current = category_repository.get_by_id(self._conn, self._selected_category_id)
        if current is None:
            return

        name, ok = QInputDialog.getText(
            self, "카테고리 이름 변경", "이름:", text=current.name
        )
        if not ok or not name.strip():
            return

        try:
            category_repository.update(
                self._conn, self._selected_category_id, name=name.strip()
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "카테고리", "같은 이름의 카테고리가 이미 있습니다.")
            return

        self.refresh()

    def _delete_category(self) -> None:
        if self._selected_category_id is None:
            QMessageBox.warning(self, "카테고리", "삭제할 카테고리를 선택하세요.")
            return

        active_count = category_repository.count_active(self._conn)
        if active_count <= 1:
            QMessageBox.warning(self, "카테고리", "마지막 카테고리는 삭제할 수 없습니다.")
            return

        reply = QMessageBox.question(
            self,
            "카테고리 삭제",
            "선택한 카테고리를 삭제할까요?\n(포함된 상용구는 유지됩니다.)",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        category_repository.soft_delete(self._conn, self._selected_category_id)
        self._conn.commit()
        self._selected_category_id = None
        self.refresh()

    def _add_snippet(self) -> None:
        category_id = self._category_combo.currentData()
        if category_id is None:
            QMessageBox.warning(self, "추가", "카테고리를 선택하세요.")
            return

        title = self._title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "추가", "제목을 입력하세요.")
            return

        snippet_repository.create_text(
            self._conn,
            category_id=int(category_id),
            title=title,
            body_text=self._body_edit.toPlainText(),
            tags=self._tags_edit.text().strip(),
        )
        self._conn.commit()
        self._selected_category_id = int(category_id)
        self._load_categories()
        self._reload_snippet_list()
        QMessageBox.information(self, "추가", "상용구가 추가되었습니다.")

    def _update_snippet(self) -> None:
        if self._selected_snippet_id is None:
            QMessageBox.warning(self, "수정", "수정할 상용구를 선택하세요.")
            return

        snippet = snippet_repository.get_by_id(self._conn, self._selected_snippet_id)
        if snippet is None:
            return

        category_id = self._category_combo.currentData()
        body = (
            snippet.body_text
            if snippet.content_type == "image"
            else self._body_edit.toPlainText()
        )
        snippet_repository.update(
            self._conn,
            self._selected_snippet_id,
            title=self._title_edit.text().strip(),
            body_text=body,
            tags=self._tags_edit.text().strip(),
            category_id=int(category_id) if category_id is not None else None,
            pinned=self._pinned_check.isChecked(),
        )
        self._conn.commit()
        if category_id is not None:
            self._selected_category_id = int(category_id)
        self._load_categories()
        self._reload_snippet_list()
        QMessageBox.information(self, "수정", "상용구가 수정되었습니다.")

    def _delete_snippet(self) -> None:
        if self._selected_snippet_id is None:
            QMessageBox.warning(self, "삭제", "삭제할 상용구를 선택하세요.")
            return
        reply = QMessageBox.question(
            self, "삭제", "선택한 상용구를 휴지통으로 이동할까요?"
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        snippet_repository.soft_delete(self._conn, self._selected_snippet_id)
        self._conn.commit()
        self._clear_detail()
        self._reload_snippet_list()

    def _restore_snippet(self) -> None:
        if self._selected_snippet_id is None:
            QMessageBox.warning(self, "복구", "복구할 상용구를 선택하세요.")
            return
        snippet_repository.restore(self._conn, self._selected_snippet_id)
        self._conn.commit()
        self._clear_detail()
        self._reload_snippet_list()
        QMessageBox.information(self, "복구", "상용구가 복구되었습니다.")

    def _empty_trash(self) -> None:
        count = snippet_repository.count_trash(self._conn)
        if count == 0:
            QMessageBox.information(self, "휴지통", "휴지통이 비어 있습니다.")
            return
        reply = QMessageBox.warning(
            self,
            "휴지통 비우기",
            f"휴지통의 {count}개 항목을 영구 삭제할까요?\n복구할 수 없습니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        removed = snippet_repository.empty_trash(self._conn)
        self._conn.commit()
        self._clear_detail()
        self._reload_snippet_list()
        QMessageBox.information(self, "휴지통", f"{removed}개 항목을 삭제했습니다.")

    def _resolve_category_id(self) -> int | None:
        category_id = self._category_combo.currentData()
        if category_id is None and self._selected_category_id is not None:
            category_id = self._selected_category_id
        return int(category_id) if category_id is not None else None

    def _prompt_title(self, default: str) -> str | None:
        title, ok = QInputDialog.getText(
            self, "상용구 제목", "제목:", text=default[:80]
        )
        if not ok or not title.strip():
            return None
        return title.strip()

    def _add_from_clipboard_text(self) -> None:
        text = QApplication.clipboard().text().strip()
        if not text:
            QMessageBox.warning(self, "클립보드", "클립보드에 텍스트가 없습니다.")
            return

        category_id = self._resolve_category_id()
        if category_id is None:
            QMessageBox.warning(self, "추가", "카테고리를 선택하세요.")
            return

        default_title = text.splitlines()[0][:40] if text else "클립보드 텍스트"
        title = self._prompt_title(default_title)
        if title is None:
            return

        snippet_repository.create_text(
            self._conn,
            category_id=category_id,
            title=title,
            body_text=text,
            tags=self._tags_edit.text().strip(),
        )
        self._conn.commit()
        self._selected_category_id = category_id
        self.refresh()
        QMessageBox.information(self, "추가", "클립보드 텍스트가 추가되었습니다.")

    def _add_image_file(self) -> None:
        category_id = self._resolve_category_id()
        if category_id is None:
            QMessageBox.warning(self, "추가", "카테고리를 선택하세요.")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 선택",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp)",
        )
        if not file_path:
            return

        path = Path(file_path)
        title = self._prompt_title(path.stem)
        if title is None:
            return

        try:
            asset_id = save_image_file(self._conn, path)
            snippet_repository.create_image(
                self._conn,
                category_id=category_id,
                title=title,
                asset_id=asset_id,
                tags=self._tags_edit.text().strip(),
            )
            self._conn.commit()
        except Exception as exc:
            QMessageBox.warning(self, "이미지 추가", f"이미지 저장 실패:\n{exc}")
            return

        self._selected_category_id = category_id
        self.refresh()
        QMessageBox.information(self, "추가", "이미지 상용구가 추가되었습니다.")

    def _add_from_clipboard_image(self) -> None:
        category_id = self._resolve_category_id()
        if category_id is None:
            QMessageBox.warning(self, "추가", "카테고리를 선택하세요.")
            return

        image = QApplication.clipboard().image()
        if image.isNull():
            QMessageBox.warning(self, "클립보드", "클립보드에 이미지가 없습니다.")
            return

        title = self._prompt_title("클립보드 이미지")
        if title is None:
            return

        try:
            asset_id = save_qimage(self._conn, image)
            snippet_repository.create_image(
                self._conn,
                category_id=category_id,
                title=title,
                asset_id=asset_id,
                tags=self._tags_edit.text().strip(),
            )
            self._conn.commit()
        except Exception as exc:
            QMessageBox.warning(self, "이미지 추가", f"클립보드 이미지 저장 실패:\n{exc}")
            return

        self._selected_category_id = category_id
        self.refresh()
        QMessageBox.information(self, "추가", "클립보드 이미지가 추가되었습니다.")
