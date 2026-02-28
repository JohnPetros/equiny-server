from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.interfaces.messages_repository import (
    MessagesRepository,
)
from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.conversation.domain.entities.message import Message
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.conversation.domain.errors import ChatNotFoundError


class SendMessageUseCase:
    def __init__(
        self,
        chats_repository: ChatsRepository,
        chat_messages_repository: MessagesRepository,
    ) -> None:
        self._chats_repository = chats_repository
        self._messages_repository = chat_messages_repository

    def execute(self, chat_message: MessageDto, chat_id: str) -> MessageDto:
        message = Message.create(chat_message)
        chat = self._find_chat(Id.create(chat_id), message.sender_id)

        self._messages_repository.add(message, chat.id)

        return message.dto

    def _find_chat(self, chat_id: Id, sender_id: Id) -> Chat:
        chat = self._chats_repository.find_by_id_and_sender_id(chat_id, sender_id)
        if not chat:
            raise ChatNotFoundError
        return chat
