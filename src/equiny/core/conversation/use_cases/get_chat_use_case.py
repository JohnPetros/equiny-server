from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.domain.errors.chat_not_found_error import (
    ChatNotFoundError,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.conversation.domain.entities.dtos import ChatDto


class GetChatUseCase:
    def __init__(self, repository: ChatsRepository) -> None:
        self._repository = repository

    def execute(self, chat_id: str, sender_id: str) -> ChatDto:
        chat = self._repository.find_by_id_and_sender_id(
            Id.create(chat_id), Id.create(sender_id)
        )
        if not chat:
            raise ChatNotFoundError
        return chat.dto
