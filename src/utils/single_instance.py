"""단일 인스턴스 실행 (중복 트레이 방지)."""

from __future__ import annotations

import logging
from collections.abc import Callable

from PySide6.QtCore import QObject
from PySide6.QtNetwork import QLocalServer, QLocalSocket

logger = logging.getLogger("quickpaste.instance")

_SERVER_NAME = "QuickPasteManager_SingleInstance_v1"


class SingleInstanceGuard(QObject):
    """첫 인스턴스만 True. 두 번째 실행 시 기존 인스턴스에 활성화 신호를 보낸다."""

    def __init__(
        self,
        *,
        on_activate: Callable[[], None] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_activate = on_activate
        self._server: QLocalServer | None = None
        self._is_primary = self._try_connect_to_running()

        if self._is_primary:
            self._start_server()

    @property
    def is_primary(self) -> bool:
        return self._is_primary

    def _try_connect_to_running(self) -> bool:
        socket = QLocalSocket()
        socket.connectToServer(_SERVER_NAME)
        if not socket.waitForConnected(400):
            return True
        socket.write(b"activate")
        socket.flush()
        socket.waitForBytesWritten(400)
        socket.disconnectFromServer()
        logger.info("이미 실행 중인 인스턴스에 활성화 신호 전송")
        return False

    def _start_server(self) -> None:
        QLocalServer.removeServer(_SERVER_NAME)
        server = QLocalServer(self)
        if not server.listen(_SERVER_NAME):
            logger.warning("단일 인스턴스 서버 시작 실패 — 중복 실행 가능")
            self._is_primary = True
            return
        server.newConnection.connect(self._on_new_connection)
        self._server = server

    def _on_new_connection(self) -> None:
        if self._server is None:
            return
        client = self._server.nextPendingConnection()
        if client is None:
            return
        client.readyRead.connect(lambda c=client: self._handle_client(c))

    def _handle_client(self, client: QLocalSocket) -> None:
        client.readAll()
        logger.info("두 번째 실행 감지 — 기존 창 활성화")
        if self._on_activate:
            self._on_activate()
