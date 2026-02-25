import contextlib
from typing import Any
from collections import defaultdict

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocketDisconnect


class Ws:
    _sockets: dict[str, WebSocket]
    _rooms: defaultdict[str, set[str]]

    def __init__(self) -> None:
        self._sockets = {}
        self._rooms = defaultdict(set)

    def count_sockets(self, key: str) -> int:
        return 1 if key in self._sockets else 0

    async def connect(self, key: str, socket: WebSocket) -> None:
        await socket.accept()
        self._sockets[key] = socket

    def disconnect(self, key: str, socket: WebSocket) -> None:
        self._sockets.pop(key, None)

    def enter_room(self, room_key: str, socket_key: str) -> None:
        self._rooms[room_key].add(socket_key)

    def leave_room(self, room_key: str, socket_key: str) -> None:
        self._rooms[room_key].discard(socket_key)

    async def send(self, socket_key: str, data: Any) -> None:
        socket = self._sockets.get(socket_key)
        if socket is None:
            return

        try:
            await socket.send_json(jsonable_encoder(data))
        except (WebSocketDisconnect, RuntimeError):
            self._sockets.pop(socket_key, None)
            with contextlib.suppress(RuntimeError):
                await socket.close()

    async def emit(self, room_key: str, data: Any) -> None:
        dead_sockets: list[tuple[str, WebSocket]] = []
        for socket_key in self._rooms[room_key]:
            socket = self._sockets.get(socket_key)
            if socket is None:
                continue

            try:
                await socket.send_json(jsonable_encoder(data))
            except (WebSocketDisconnect, RuntimeError):
                dead_sockets.append((socket_key, socket))

        for socket_key, socket in dead_sockets:
            self._sockets.pop(socket_key, None)
            with contextlib.suppress(RuntimeError):
                await socket.close()
