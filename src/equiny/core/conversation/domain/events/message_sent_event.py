from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    message_content: str
    chat_id: str
    sender_id: str


class MessageSentEvent(Event[Payload]):
    name: str = 'conversation/message.sent'

    def __init__(self, message_content: str, chat_id: str, sender_id: str) -> None:
        payload = Payload(
            message_content=message_content,
            chat_id=chat_id,
            sender_id=sender_id,
        )
        super().__init__(MessageSentEvent.name, payload)
