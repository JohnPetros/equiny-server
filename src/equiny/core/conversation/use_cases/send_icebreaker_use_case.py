from equiny.core.conversation.domain.events.icebreak_sent_event import IcebreakSentEvent
from equiny.core.profiling.interfaces.repositories.horsers_repository import (
    HorsesRepository,
)
from equiny.core.shared.interfaces.broker import Broker


class SendIcebreakerUseCase:
    def __init__(self, repository: HorsesRepository, broker: Broker) -> None:
        self._repository = repository
        self._broker = broker

    def execute(
        self, sender_horse_id: str, recipient_horse_id: str, icebreaker: str
    ) -> None:
        event = IcebreakSentEvent(
            icebreaker=icebreaker,
            sender_id=sender_horse_id,
            recipient_id=recipient_horse_id,
        )
        self._broker.publish(event)
