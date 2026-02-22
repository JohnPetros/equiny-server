from sqlalchemy.orm import joinedload

from equiny.core.conversation.domain.entities.message import Message
from equiny.core.conversation.interfaces.messages_repository import MessagesRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.integer import Integer
from equiny.core.shared.responses.pagination_response import PaginationResponse
from equiny.database.sqlalchemy.mappers.conversation.messages_mapper import (
    MessagesMapper,
)
from equiny.database.sqlalchemy.models.conversation.message_model import MessageModel
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)


class SqlalchemyMessagesRepository(SqlalchemyRepository, MessagesRepository):
    def add(self, message: Message, chat_id: Id) -> None:
        model = MessagesMapper.to_model(message, chat_id.value)
        self.sqlalchemy.add(model)

    def find_by_chat_id_and_sender_id(
        self,
        chat_id: Id,
        sender_id: Id,
    ) -> Message:
        model = (
            self.sqlalchemy.query(MessageModel)
            .options(joinedload(MessageModel.attachments))
            .filter(
                MessageModel.chat_id == chat_id.value,
                MessageModel.sender_id == sender_id.value,
            )
            .first()
        )
        if model is None:
            raise ValueError('Message not found')

        return MessagesMapper.to_entity(model)

    def find_many_by_chat_id_and_sender_id(
        self,
        chat_id: Id,
        sender_id: Id,
        cursor: Id | None,
        limit: Integer,
    ) -> PaginationResponse[Message]:
        query = (
            self.sqlalchemy.query(MessageModel)
            .options(joinedload(MessageModel.attachments))
            .filter(
                MessageModel.chat_id == chat_id.value,
            )
        )

        if cursor is not None:
            query = query.filter(MessageModel.id < cursor.value)

        models = query.order_by(MessageModel.id.desc()).limit(limit.value + 1).all()

        has_more = len(models) > limit.value
        if has_more:
            models = models[: limit.value]

        messages = [MessagesMapper.to_entity(model) for model in models]
        next_cursor = messages[-1].id.value if has_more else None

        return PaginationResponse(
            items=messages,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    def mark_read_by_recipient(self, chat_id: Id, recipient_id: Id) -> None:
        (
            self.sqlalchemy.query(MessageModel)
            .filter(
                MessageModel.chat_id == chat_id.value,
                MessageModel.sender_id != recipient_id.value,
                MessageModel.is_read_by_recipient.is_(False),
            )
            .update({MessageModel.is_read_by_recipient: True})
        )
