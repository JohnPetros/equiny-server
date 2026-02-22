from sqlalchemy import Label, and_, func
from sqlalchemy.orm import joinedload, selectinload

from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.database.sqlalchemy.mappers.conversation.chats_mapper import ChatsMapper
from equiny.database.sqlalchemy.models.conversation.chat_model import ChatModel
from equiny.database.sqlalchemy.models.conversation.message_model import MessageModel
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)


class SqlalchemyChatsRepository(SqlalchemyRepository, ChatsRepository):
    def add(self, chat: Chat, sender_id: Id) -> None:
        model = ChatsMapper.to_model(chat, sender_id.value)
        self.sqlalchemy.add(model)

    def find_many_by_sender_id(self, sender_id: Id) -> list[Chat]:
        unread_messages_count = self._count_unread_messages(sender_id.value)

        rows = (
            self.sqlalchemy.query(ChatModel, unread_messages_count)
            .options(selectinload(ChatModel.owner_a), selectinload(ChatModel.owner_b))
            .outerjoin(MessageModel, MessageModel.chat_id == ChatModel.id)
            .filter(
                (ChatModel.owner_a_id == sender_id.value)
                | (ChatModel.owner_b_id == sender_id.value)
            )
            .group_by(ChatModel.id)
            .all()
        )

        chat_ids = [model.id for model, _ in rows]
        last_messages = self._find_last_messages_by_chat_ids(chat_ids)

        return [
            ChatsMapper.to_entity(
                model, sender_id.value, unread_count, last_messages.get(model.id)
            )
            for model, unread_count in rows
        ]

    def find_by_recipient_id_and_sender_id(
        self, recipient_id: Id, sender_id: Id
    ) -> Chat | None:
        model = (
            self.sqlalchemy.query(ChatModel)
            .options(joinedload(ChatModel.owner_a), joinedload(ChatModel.owner_b))
            .filter(
                (
                    (ChatModel.owner_a_id == sender_id.value)
                    & (ChatModel.owner_b_id == recipient_id.value)
                )
                | (
                    (ChatModel.owner_a_id == recipient_id.value)
                    & (ChatModel.owner_b_id == sender_id.value)
                )
            )
            .first()
        )
        if model is None:
            return None
        last_message = self._find_last_message_by_chat_id(model.id)
        return ChatsMapper.to_entity(model, sender_id.value, last_message=last_message)

    def find_by_id_and_participant_id(
        self, chat_id: Id, participant_id: Id
    ) -> Chat | None:
        model = (
            self.sqlalchemy.query(ChatModel)
            .options(joinedload(ChatModel.owner_a), joinedload(ChatModel.owner_b))
            .filter(
                ChatModel.id == chat_id.value,
                (ChatModel.owner_a_id == participant_id.value)
                | (ChatModel.owner_b_id == participant_id.value),
            )
            .first()
        )
        if model is None:
            return None
        last_message = self._find_last_message_by_chat_id(model.id)
        return ChatsMapper.to_entity(
            model, participant_id.value, last_message=last_message
        )

    def find_by_id_and_sender_id(self, chat_id: Id, sender_id: Id) -> Chat | None:
        return self.find_by_id_and_participant_id(chat_id, sender_id)

    def _count_unread_messages(self, sender_id: str) -> Label[int]:
        return (
            func.count(MessageModel.id)
            .filter(
                MessageModel.sender_id != sender_id,
                MessageModel.is_read_by_recipient.is_(False),
            )
            .label('unread_messages_count')
        )

    def _find_last_message_by_chat_id(self, chat_id: str) -> MessageDto | None:
        message = (
            self.sqlalchemy.query(MessageModel)
            .filter(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.sent_at.desc())
            .first()
        )
        return ChatsMapper.build_message_dto(message)

    def _find_last_messages_by_chat_ids(
        self, chat_ids: list[str]
    ) -> dict[str, MessageDto | None]:
        if not chat_ids:
            return {}

        latest_messages = (
            self.sqlalchemy.query(
                MessageModel.chat_id,
                func.max(MessageModel.sent_at).label('max_sent_at'),
            )
            .filter(MessageModel.chat_id.in_(chat_ids))
            .group_by(MessageModel.chat_id)
            .subquery()
        )

        messages = (
            self.sqlalchemy.query(MessageModel)
            .join(
                latest_messages,
                and_(
                    MessageModel.chat_id == latest_messages.c.chat_id,
                    MessageModel.sent_at == latest_messages.c.max_sent_at,
                ),
            )
            .all()
        )

        return {
            message.chat_id: ChatsMapper.build_message_dto(message)
            for message in messages
        }
