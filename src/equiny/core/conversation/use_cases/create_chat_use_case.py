from equiny.core.conversation.domain.errors.chat_already_exists_error import (
    ChatAlreadyExistsError,
)
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto
from equiny.core.shared.domain.structures.id import Id


class CreateChatUseCase:
    def __init__(
        self,
        chats_repository: ChatsRepository,
    ) -> None:
        self._repository = chats_repository

    def execute(self, recipient_id: str, sender_id: str) -> ChatDto:
        chat = Chat.create(
            ChatDto(
                recipient=RecipientDto(id=recipient_id, name='fnjifnvjifdnvjifn'),
                unread_messages_count=0,
            )
        )
        sender_id_obj = Id.create(sender_id)
        self._find_chat(chat.recipient.id, sender_id_obj)
        self._repository.add(chat, sender_id_obj)
        return chat.dto

    def _find_chat(self, recipient_id: Id, sender_id: Id) -> None:
        chat = self._repository.find_by_recipient_id_and_sender_id(
            recipient_id=recipient_id,
            sender_id=sender_id,
        )
        if chat:
            raise ChatAlreadyExistsError
