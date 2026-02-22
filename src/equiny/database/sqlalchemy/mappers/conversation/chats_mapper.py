from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto
from equiny.core.shared.domain.structures.dtos.image_dto import ImageDto
from equiny.database.sqlalchemy.mappers.conversation.attachments_mapper import (
    AttachmentsMapper,
)
from equiny.database.sqlalchemy.models.conversation.chat_model import ChatModel
from equiny.database.sqlalchemy.models.conversation.message_model import MessageModel
from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel


class ChatsMapper:
    @staticmethod
    def to_entity(
        model: ChatModel,
        sender_id: str,
        unread_messages_count: int = 0,
        last_message: MessageDto | None = None,
    ) -> Chat:
        recipient_model = (
            model.owner_b if model.owner_a_id == sender_id else model.owner_a
        )
        recipient_dto = RecipientDto(
            id=recipient_model.id,
            name=recipient_model.name,
            avatar=ChatsMapper._build_avatar_dto(recipient_model),
            last_presence_at=recipient_model.last_presence_at,
        )
        dto = ChatDto(
            id=model.id,
            recipient=recipient_dto,
            unread_messages_count=unread_messages_count,
            last_message=last_message,
        )
        return Chat.create(dto)

    @staticmethod
    def to_model(chat: Chat, sender_id: str) -> ChatModel:
        recipient_id = chat.recipient.id.value
        return ChatModel(
            id=chat.id.value,
            owner_a_id=sender_id,
            owner_b_id=recipient_id,
        )

    @staticmethod
    def _build_avatar_dto(owner_model: OwnerModel) -> ImageDto | None:
        if owner_model.avatar_key is None:
            return None
        return ImageDto(
            key=owner_model.avatar_key,
            name=owner_model.avatar_name or '',
        )

    @staticmethod
    def build_message_dto(model: MessageModel | None) -> MessageDto | None:
        if model is None:
            return None
        return MessageDto(
            id=model.id,
            sender_id=model.sender_id,
            content=model.content,
            attachments=[
                AttachmentsMapper.to_entity(attachment).dto
                for attachment in model.attachments
            ],
            sent_at=model.sent_at,
            updated_at=model.updated_at,
            is_read_by_recipient=model.is_read_by_recipient,
        )
