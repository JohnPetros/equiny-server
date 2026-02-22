from equiny.core.conversation.interfaces.messages_repository import (
    MessagesRepository,
)
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.integer import Integer
from equiny.core.conversation.domain.errors import ChatNotFoundError
from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.shared.responses.pagination_response import PaginationResponse


class ListMessagesUseCase:
    def __init__(
        self,
        chats_repository: ChatsRepository,
        messages_repository: MessagesRepository,
    ) -> None:
        self._chats_repository = chats_repository
        self._messages_repository = messages_repository

    def execute(
        self,
        chat_id: str,
        sender_id: str,
        cursor: str | None = None,
        limit: int = 20,
    ) -> PaginationResponse[MessageDto]:
        chat = self._find_chat(Id.create(chat_id), Id.create(sender_id))
        self._messages_repository.mark_read_by_recipient(
            chat.id,
            Id.create(sender_id),
        )
        pagination = self._messages_repository.find_many_by_chat_id_and_sender_id(
            chat.id,
            Id.create(sender_id),
            Id.create(cursor) if cursor else None,
            Integer.create(limit),
        )
        return pagination.map_items(lambda message: message.dto)

    def _find_chat(self, chat_id: Id, sender_id: Id) -> Chat:
        chat = self._chats_repository.find_by_id_and_sender_id(chat_id, sender_id)
        if not chat:
            raise ChatNotFoundError
        return chat
