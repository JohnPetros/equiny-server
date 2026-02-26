from typing import Any
from asyncio import create_task

from equiny.core.conversation.domain.events import MessageReceivedEvent
from equiny.core.shared.domain.abstracts import Event

from equiny.pubsub.redis.brokers.redis_broker import RedisBroker


class RedisConversationBroker(RedisBroker):
    def publish(self, event: Event[Any]) -> None:
        if isinstance(event, MessageReceivedEvent):
            self._publish_message_received_event(event)

    def _publish_message_received_event(self, event: MessageReceivedEvent) -> None:
        create_task(
            self.pubsub.publish(
                socket_key=event.payload.recipient_id,
                action='emit',
                event=event,
            )
        )
        create_task(
            self.pubsub.publish(
                socket_key=event.payload.message.sender_id,
                action='emit',
                event=event,
            )
        )
