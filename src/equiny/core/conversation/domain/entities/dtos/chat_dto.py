from equiny.core.shared.domain.decorators import dto
from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto


@dto
class ChatDto:
    id: str | None = None
    recipient: RecipientDto
    unread_messages_count: int
    last_message: MessageDto | None = None
