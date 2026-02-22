from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.conversation.domain.entities.message import Message
from equiny.database.sqlalchemy.mappers.conversation.attachments_mapper import (
    AttachmentsMapper,
)
from equiny.database.sqlalchemy.models.conversation.message_model import MessageModel


class MessagesMapper:
    @staticmethod
    def to_entity(model: MessageModel) -> Message:
        dto = MessageDto(
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
        return Message.create(dto)

    @staticmethod
    def to_model(message: Message, chat_id: str) -> MessageModel:
        dto = message.dto
        print('dto', dto)
        model = MessageModel(
            id=dto.id,
            chat_id=chat_id,
            sender_id=dto.sender_id,
            content=dto.content,
            is_read_by_recipient=dto.is_read_by_recipient or False,
            sent_at=dto.sent_at,
        )
        model.attachments = [
            AttachmentsMapper.to_model(attachment, model.id)
            for attachment in message.attachments
        ]
        return model
