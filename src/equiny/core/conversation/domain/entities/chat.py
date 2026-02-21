from equiny.core.shared.domain.decorators import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.shared.domain.structures.id import Id
from equiny.core.conversation.domain.entities.message import Message
from equiny.core.conversation.domain.entities.recipient import Recipient
from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.shared.domain.structures.integer import Integer


@entity
class Chat(Entity):
    recipient: Recipient
    unread_messages_count: Integer
    last_message: Message | None = None

    @classmethod
    def create(cls, dto: ChatDto) -> 'Chat':
        return cls(
            id=Id.create(dto.id),
            recipient=Recipient.create(dto.recipient),
            unread_messages_count=Integer.create(dto.unread_messages_count),
            last_message=Message.create(dto.last_message) if dto.last_message else None,
        )

    @property
    def dto(self) -> ChatDto:
        return ChatDto(
            id=self.id.value,
            recipient=self.recipient.dto,
            unread_messages_count=self.unread_messages_count.value,
            last_message=self.last_message.dto if self.last_message else None,
        )
