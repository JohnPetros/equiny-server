import asyncio
from datetime import datetime
import json
import contextlib
from dataclasses import asdict
from typing import Any, Literal, cast

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from equiny.core.shared.domain.abstracts.event import Event
from equiny.constants import Env
from equiny.websocket import ws

WsAction = Literal['emit', 'broadcast']


class RedisPubSub:
    pubsub: PubSub | None = None
    client: Redis | None = None
    task: asyncio.Task[None] | None = None
    app_channel: str = 'equiny'

    async def start(self) -> None:
        redis = Redis.from_url(Env.REDIS_URL)  # type: ignore[reportUnknownMemberType]
        self.client = redis
        self.pubsub = redis.pubsub()  # type: ignore[reportUnknownMemberType]
        await self.pubsub.psubscribe(f'{self.app_channel}:*')
        self.task = asyncio.create_task(self.reader())

    async def stop(self) -> None:
        if self.task is not None:
            self.task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.task
            self.task = None

        if self.pubsub is not None:
            await self.pubsub.aclose()
            self.pubsub = None

        self.client = None

    async def reader(self) -> None:
        if self.pubsub is None:
            return

        while True:
            message = cast(
                'dict[str, Any] | None',
                await self.pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                ),
            )
            if not message:
                await asyncio.sleep(0.01)
                continue

            data = self._parse_data(message.get('data'))
            if data is None:
                continue

            action = cast('str | None', data.get('action'))
            socket_key = cast('str | None', data.get('socket_key'))
            event = data.get('event')

            if action is None or socket_key is None:
                continue

            match action:
                case 'emit':
                    await ws.emit(socket_key, event)
                case _:
                    pass

    async def publish(
        self, socket_key: str, action: WsAction, event: Event[Any]
    ) -> None:
        if self.client is None:
            return
        data: dict[str, Any] = {}
        data['action'] = action
        data['socket_key'] = socket_key
        data['event'] = self._parse_event(event)
        await self.client.publish(  # type: ignore[reportUnknownMemberType]
            f'{self.app_channel}:{socket_key}', json.dumps(data)
        )

    def _parse_event(self, event: Event[Any]) -> dict[str, Any]:
        def _make_json_serializable(obj: Any) -> Any:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, dict):
                return {k: _make_json_serializable(v) for k, v in obj.items()}  # type: ignore[reportUnknownReturnType]
            if isinstance(obj, (list, tuple)):
                return [_make_json_serializable(i) for i in obj]  # type: ignore[reportUnknownReturnType]
            return obj

        return cast('dict[str, Any]', _make_json_serializable(asdict(event)))

    @staticmethod
    def _parse_data(data: Any) -> dict[str, Any] | None:
        if isinstance(data, (bytes, bytearray)):
            data = data.decode()

        if isinstance(data, str):
            try:
                decoded = json.loads(data)
            except json.JSONDecodeError:
                return None

            if isinstance(decoded, dict):
                return cast('dict[str, Any]', decoded)
            return None

        if isinstance(data, dict):
            return cast('dict[str, Any]', data)

        return None
