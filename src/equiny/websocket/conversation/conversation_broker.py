from typing import Any
from asyncio import create_task

from equiny.constants import ROOMS_KEYS
from equiny.core.conversation.domain.events import MessageReceivedEvent
from equiny.core.shared.domain.abstracts import Event
from equiny.core.shared.interfaces.broker import Broker
from equiny.websocket.ws import Ws


class ConversationBroker(Broker):
    def __init__(self, ws: Ws) -> None:
        self._ws = ws

    def publish(self, event: Event[Any]) -> None:
        print('event', f'{ROOMS_KEYS.CHAT}:{event.payload.chat_id}')
        if isinstance(event, MessageReceivedEvent):
            create_task(
                self._ws.emit(
                    f'{ROOMS_KEYS.CHAT}:{event.payload.chat_id}',
                    event,
                )
            )
