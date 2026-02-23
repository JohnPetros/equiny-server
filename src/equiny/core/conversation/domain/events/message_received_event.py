from dataclasses import dataclass
from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    message: MessageDto
    chat_id: str


class MessageReceivedEvent(Event[Payload]):
    name: str = 'conversation/message.received'

    def __init__(self, message: MessageDto, chat_id: str) -> None:
        payload = Payload(
            message=message,
            chat_id=chat_id,
        )
        super().__init__(MessageReceivedEvent.name, payload)
