import asyncio
import json
import contextlib
from dataclasses import asdict
from typing import Any, Literal, cast

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from equiny.core.shared.domain.abstracts.event import Event
from equiny.constants import Env
from equiny.websocket import ws

WsAction = Literal['emit', 'send']


class RedisPubSub:
    pubsub: PubSub | None = None
    client: Redis | None = None
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

            print('message', message)
            data = message['data']
            action = cast('str', data['action'])
            connection_key = data['connection_key']
            event = data['event']

            match action:
                case 'emit':
                    await ws.emit(connection_key, event)
                case 'send':
                    await ws.send(connection_key, event)
                case _:
                    pass

    async def publish(
        self, connection_key: str, action: WsAction, event: Event[Any]
    ) -> None:
        if self.client is None:
            return
        data: dict[str, Any] = {}
        data['action'] = action
        data['connection_key'] = connection_key
        data['event'] = asdict(event)
        await self.client.publish(  # type: ignore[reportUnknownMemberType]
            f'{self.app_channel}:{connection_key}', json.dumps(data)
        )
