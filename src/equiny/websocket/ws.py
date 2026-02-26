import contextlib
from typing import Any

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocketDisconnect


class Ws:
    _sockets: dict[str, WebSocket]

    def __init__(self) -> None:
        self._sockets = {}

    def count_sockets(self, key: str) -> int:
        return 1 if key in self._sockets else 0

    async def connect(self, key: str, socket: WebSocket) -> None:
        await socket.accept()
        self._sockets[key] = socket
        print('socket connected', key)

    def disconnect(self, key: str, socket: WebSocket) -> None:
        self._sockets.pop(key, None)

    async def emit(self, socket_key: str, data: Any) -> None:
        socket = self._sockets.get(socket_key)
        if socket is None:
            return

        try:
            await socket.send_json(jsonable_encoder(data))
        except (WebSocketDisconnect, RuntimeError):
            self._sockets.pop(socket_key, None)
            with contextlib.suppress(RuntimeError):
                await socket.close()
