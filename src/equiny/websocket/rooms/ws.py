from typing import Any
from dataclasses import asdict

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocketDisconnect


class Ws:
    _sockets: set[WebSocket]

    def __init__(self) -> None:
        self._sockets: set[WebSocket] = set()

    async def connect(self, socket: WebSocket) -> None:
        await socket.accept()
        self._sockets.add(socket)

    def disconnect(self, socket: WebSocket) -> None:
        self._sockets.discard(socket)

    async def broadcast(self, data: Any) -> None:
        dead_sockets: list[WebSocket] = []
        for socket in self._sockets:
            try:
                await socket.send_json(jsonable_encoder(asdict(data)))
            except (WebSocketDisconnect, RuntimeError):
                dead_sockets.append(socket)

        for socket in dead_sockets:
            self.disconnect(socket)
