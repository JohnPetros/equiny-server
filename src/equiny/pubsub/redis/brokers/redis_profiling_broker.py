from typing import Any
from asyncio import create_task

from equiny.core.profiling.domain.events import (
    OwnerPresenceRegisteredEvent,
    OwnerPresenceUnregisteredEvent,
)
from equiny.core.shared.domain.abstracts.event import Event
from equiny.pubsub.redis.brokers.redis_broker import RedisBroker


class RedisProfilingBroker(RedisBroker):
    def publish(self, event: Event[Any]) -> None:

        if isinstance(event, OwnerPresenceRegisteredEvent):
            self._publish_owner_presence_registered_event(event)
        if isinstance(event, OwnerPresenceUnregisteredEvent):
            self._publish_owner_presence_unregistered_event(event)

    def _publish_owner_presence_registered_event(
        self, event: OwnerPresenceRegisteredEvent
    ) -> None:
        for owner_match in event.payload.owner_matches:
            create_task(
                self.pubsub.publish(
                    socket_key=owner_match,
                    action='emit',
                    event=event,
                )
            )

    def _publish_owner_presence_unregistered_event(
        self, event: OwnerPresenceUnregisteredEvent
    ) -> None:
        for owner_match in event.payload.owner_matches:
            create_task(
                self.pubsub.publish(
                    socket_key=owner_match,
                    action='emit',
                    event=event,
                )
            )
