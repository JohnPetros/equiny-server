from typing import Any
from dataclasses import asdict
from collections import defaultdict

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocketDisconnect


class Ws:
    _sockets: defaultdict[str, WebSocket]
    _rooms: defaultdict[str, set[str]]

    def __init__(self) -> None:
        self._sockets = defaultdict()
        self._rooms = defaultdict(set)

    def count_sockets(self, key: str) -> int:
        return len(self._sockets[key])

    async def connect(self, key: str, socket: WebSocket) -> None:
        await socket.accept()
        self._sockets[key] = socket

    def disconnect(self, key: str, socket: WebSocket) -> None:
        del self._sockets[key]

    def enter_room(self, room_key: str, socket_key: str) -> None:
        self._rooms[room_key].add(socket_key)

    def leave_room(self, room_key: str, socket_key: str) -> None:
        self._rooms[room_key].discard(socket_key)

    async def send(self, socket_key: str, data: Any) -> None:
        try:
            socket = self._sockets[socket_key]
            await socket.send_json(jsonable_encoder(asdict(data)))
        except (WebSocketDisconnect, RuntimeError):
            await self._sockets[socket_key].close()

    async def emit(self, room_key: str, data: Any) -> None:
        dead_sockets: list[WebSocket] = []
        print(self._rooms)
        print(self._rooms[room_key])
        for socket_key in self._rooms[room_key]:
            try:
                socket = self._sockets[socket_key]
                await socket.send_json(jsonable_encoder(asdict(data)))
            except (WebSocketDisconnect, RuntimeError):
                dead_sockets.append(self._sockets[socket_key])

        for socket in dead_sockets:
            await socket.close()
