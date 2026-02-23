from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    participant_id: str
    chat_id: str


class ChatOwnerEnteredEvent(Event[Payload]):
    name: str = 'conversation/chat.participant.entered'

    def __init__(self, participant_id: str, chat_id: str) -> None:
        payload = Payload(
            participant_id=participant_id,
            chat_id=chat_id,
        )
        super().__init__(ChatOwnerEnteredEvent.name, payload)
