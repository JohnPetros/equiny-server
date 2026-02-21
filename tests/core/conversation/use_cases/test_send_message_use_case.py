import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto
from equiny.core.conversation.domain.errors.chat_not_found_error import (
    ChatNotFoundError,
)
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.interfaces.messages_repository import MessagesRepository
from equiny.core.conversation.use_cases.send_message_use_case import SendMessageUseCase
from equiny.core.shared.domain.structures.id import Id
from tests.fakers.shared.structures.id_faker import IdFaker


class TestSendMessageUseCase:
    chats_repository_mock: Mock
    messages_repository_mock: Mock
    use_case: SendMessageUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.chats_repository_mock = create_autospec(ChatsRepository, instance=True)
        self.messages_repository_mock = create_autospec(
            MessagesRepository,
            instance=True,
        )
        self.use_case = SendMessageUseCase(
            chats_repository=self.chats_repository_mock,
            chat_messages_repository=self.messages_repository_mock,
        )

    def test_should_create_message_and_add_it_to_repository_when_chat_exists(
        self,
    ) -> None:
        sender_id = IdFaker.fake().value
        chat = Chat.create(
            ChatDto(
                recipient=RecipientDto(id=IdFaker.fake().value, name='Recipient'),
                unread_messages_count=0,
            )
        )
        self.chats_repository_mock.find_by_id_and_sender_id.return_value = chat
        message_dto = MessageDto(
            sender_id=sender_id,
            content='Hello there',
            attachments=[],
        )

        result = self.use_case.execute(chat_message=message_dto, chat_id=chat.id.value)

        self.chats_repository_mock.find_by_id_and_sender_id.assert_called_once_with(
            Id.create(chat.id.value),
            Id.create(sender_id),
        )
        self.messages_repository_mock.add.assert_called_once()
        added_message, added_chat_id = self.messages_repository_mock.add.call_args.args
        assert added_chat_id == chat.id
        assert result == added_message.dto
        assert result.content == 'Hello there'

    def test_should_raise_chat_not_found_error_when_chat_does_not_exist(self) -> None:
        chat_id = IdFaker.fake().value
        sender_id = IdFaker.fake().value
        self.chats_repository_mock.find_by_id_and_sender_id.return_value = None
        message_dto = MessageDto(
            sender_id=sender_id,
            content='Hello there',
            attachments=[],
        )

        with pytest.raises(ChatNotFoundError):
            self.use_case.execute(chat_message=message_dto, chat_id=chat_id)

        self.messages_repository_mock.add.assert_not_called()
