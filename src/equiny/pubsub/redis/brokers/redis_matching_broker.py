from typing import Any
from asyncio import create_task

from equiny.core.profiling.domain.events import HorseMatchNotifiedEvent
from equiny.core.shared.domain.abstracts import Event

from equiny.pubsub.redis.brokers.redis_broker import RedisBroker


class RedisMatchingBroker(RedisBroker):
    def publish(self, event: Event[Any]) -> None:
        if isinstance(event, HorseMatchNotifiedEvent):
            self._publish_horse_match_notified_event(event)

    def _publish_horse_match_notified_event(
        self, event: HorseMatchNotifiedEvent
    ) -> None:
        owner_id = event.payload.horse_match.owner_id
        create_task(
            self.pubsub.publish_for_socket(
                socket_key=owner_id,
                action='emit',
                event=event,
            )
        )
