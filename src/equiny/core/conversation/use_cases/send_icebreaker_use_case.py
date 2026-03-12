from equiny.core.conversation.domain.events.icebreaker_sent_event import (
    IcebreakerSentEvent,
)
from equiny.core.shared.interfaces.broker import Broker


class SendIcebreakerUseCase:
    def __init__(self, broker: Broker) -> None:
        self._broker = broker

    def execute(
        self, sender_horse_id: str, recipient_horse_id: str, icebreaker: str
    ) -> None:
        event = IcebreakerSentEvent(
            icebreaker=icebreaker,
            sender_id=sender_horse_id,
            recipient_id=recipient_horse_id,
        )
        self._broker.publish(event)
