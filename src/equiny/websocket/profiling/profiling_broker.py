from typing import Any
from asyncio import Task, create_task

from equiny.core.shared.domain.abstracts import Event
from equiny.core.shared.interfaces.broker import Broker
from equiny.websocket.ws import Ws
from equiny.constants import ROOMS_KEYS
from equiny.core.profiling.domain.events import OwnerPresenceRegisteredEvent


class ProfilingBroker(Broker):
    def __init__(self, ws: Ws) -> None:
        self._ws = ws
        self._background_tasks: set[Task[Any]] = set()

    def publish(self, event: Event[Any]) -> None:
        if isinstance(event, OwnerPresenceRegisteredEvent):
            create_task(
                self._ws.emit(
                    f'{ROOMS_KEYS.INBOX}:{event.payload.owner_id}',
                    event,
                )
            )
