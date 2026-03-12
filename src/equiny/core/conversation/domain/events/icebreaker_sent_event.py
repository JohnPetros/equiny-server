from dataclasses import dataclass

from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    icebreaker: str
    sender_id: str
    recipient_id: str


class IcebreakerSentEvent(Event[Payload]):
    name: str = 'conversation/icebreaker.sent'

    def __init__(self, icebreaker: str, sender_id: str, recipient_id: str) -> None:
        payload = Payload(
            icebreaker=icebreaker,
            sender_id=sender_id,
            recipient_id=recipient_id,
        )
        super().__init__(IcebreakerSentEvent.name, payload)
