from typing import Any
from dataclasses import asdict
from collections import defaultdict

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocketDisconnect


class Ws:
    _channels: defaultdict[str, set[WebSocket]]

    def __init__(self) -> None:
        self._channels = defaultdict(set)

    def count_sockets(self, key: str) -> int:
        return len(self._channels[key])

    async def connect(self, key: str, socket: WebSocket) -> None:
        await socket.accept()
        self._channels[key].add(socket)

    def disconnect(self, key: str, socket: WebSocket) -> None:
        self._channels[key].discard(socket)

    async def broadcast(self, key: str, data: Any) -> None:
        dead_sockets: list[WebSocket] = []
        for socket in self._channels[key]:
            try:
                await socket.send_json(jsonable_encoder(asdict(data)))
            except (WebSocketDisconnect, RuntimeError):
                dead_sockets.append(socket)

        for socket in dead_sockets:
            self.disconnect(key, socket)
