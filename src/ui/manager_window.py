"""상용구 관리 창 뼈대."""

from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
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

from src.repositories import category_repository, snippet_repository


class ManagerWindow(QMainWindow):
    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__()
        self._conn = conn
        self._selected_category_id: int | None = None
        self._selected_snippet_id: int | None = None

        self.setWindowTitle("QuickPaste Manager — 상용구 관리")
        self.resize(900, 600)
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("검색 / 필터...")
        self._search.textChanged.connect(self._on_search)
        search_row.addWidget(self._search)
        root.addLayout(search_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 좌측: 카테고리
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("카테고리"))
        self._category_list = QListWidget()
        self._category_list.currentItemChanged.connect(self._on_category_selected)
        left_layout.addWidget(self._category_list)
        splitter.addWidget(left)

        # 중앙: 상용구 목록
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.addWidget(QLabel("상용구 목록"))
        self._snippet_list = QListWidget()
        self._snippet_list.currentItemChanged.connect(self._on_snippet_selected)
        center_layout.addWidget(self._snippet_list)
        splitter.addWidget(center)

        # 우측: 상세 편집
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("상세 편집"))
        form = QFormLayout()
        self._title_edit = QLineEdit()
        self._tags_edit = QLineEdit()
        self._body_edit = QTextEdit()
        form.addRow("제목", self._title_edit)
        form.addRow("태그", self._tags_edit)
        form.addRow("본문", self._body_edit)
        right_layout.addLayout(form)
        splitter.addWidget(right)

        splitter.setSizes([200, 300, 400])
        root.addWidget(splitter)

        btn_row = QHBoxLayout()
        self._add_btn = QPushButton("추가")
        self._update_btn = QPushButton("수정")
        self._delete_btn = QPushButton("삭제")
        self._restore_btn = QPushButton("복구")
        self._restore_btn.setEnabled(False)  # TODO: 휴지통 복구

        self._add_btn.clicked.connect(self._add_snippet)
        self._update_btn.clicked.connect(self._update_snippet)
        self._delete_btn.clicked.connect(self._delete_snippet)

        for btn in (self._add_btn, self._update_btn, self._delete_btn, self._restore_btn):
            btn_row.addWidget(btn)
        root.addLayout(btn_row)

    def refresh(self) -> None:
        self._load_categories()
        if self._selected_category_id:
            self._load_snippets(self._selected_category_id)

    def _load_categories(self) -> None:
        self._category_list.clear()
        for cat in category_repository.list_active(self._conn):
            item = QListWidgetItem(cat.name)
            item.setData(Qt.ItemDataRole.UserRole, cat.id)
            self._category_list.addItem(item)

    def _load_snippets(self, category_id: int) -> None:
        self._snippet_list.clear()
        for snippet in snippet_repository.list_by_category(self._conn, category_id):
            item = QListWidgetItem(snippet.title)
            item.setData(Qt.ItemDataRole.UserRole, snippet.id)
            self._snippet_list.addItem(item)

    def _on_category_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            return
        self._selected_category_id = current.data(Qt.ItemDataRole.UserRole)
        self._load_snippets(self._selected_category_id)
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
        self._body_edit.setPlainText(snippet.body_text or "")

    def _clear_detail(self) -> None:
        self._selected_snippet_id = None
        self._title_edit.clear()
        self._tags_edit.clear()
        self._body_edit.clear()

    def _on_search(self, text: str) -> None:
        if not text.strip():
            if self._selected_category_id:
                self._load_snippets(self._selected_category_id)
            return
        self._snippet_list.clear()
        for snippet in snippet_repository.search(self._conn, text.strip()):
            item = QListWidgetItem(snippet.title)
            item.setData(Qt.ItemDataRole.UserRole, snippet.id)
            self._snippet_list.addItem(item)

    def _add_snippet(self) -> None:
        if self._selected_category_id is None:
            QMessageBox.warning(self, "추가", "카테고리를 먼저 선택하세요.")
            return
        title = self._title_edit.text().strip()
        body = self._body_edit.toPlainText()
        if not title:
            QMessageBox.warning(self, "추가", "제목을 입력하세요.")
            return
        snippet_repository.create_text(
            self._conn,
            category_id=self._selected_category_id,
            title=title,
            body_text=body,
            tags=self._tags_edit.text().strip(),
        )
        self._conn.commit()
        self._load_snippets(self._selected_category_id)
        QMessageBox.information(self, "추가", "상용구가 추가되었습니다.")

    def _update_snippet(self) -> None:
        if self._selected_snippet_id is None:
            QMessageBox.warning(self, "수정", "수정할 상용구를 선택하세요.")
            return
        snippet_repository.update(
            self._conn,
            self._selected_snippet_id,
            title=self._title_edit.text().strip(),
            body_text=self._body_edit.toPlainText(),
            tags=self._tags_edit.text().strip(),
        )
        self._conn.commit()
        if self._selected_category_id:
            self._load_snippets(self._selected_category_id)
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
        if self._selected_category_id:
            self._load_snippets(self._selected_category_id)
