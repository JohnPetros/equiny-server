import pytest
from unittest.mock import MagicMock, create_autospec

from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto
from equiny.core.conversation.domain.errors.chat_not_found_error import (
    ChatNotFoundError,
)
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases.get_chat_use_case import GetChatUseCase
from equiny.core.shared.domain.structures.id import Id
from tests.fakers.shared.structures.id_faker import IdFaker


class TestGetChatUseCase:
    repository_mock: MagicMock
    use_case: GetChatUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(ChatsRepository, instance=True)
        self.use_case = GetChatUseCase(repository=self.repository_mock)

    def test_should_return_chat_dto_when_chat_exists(self) -> None:
        sender_id = IdFaker.fake().value
        chat = Chat.create(
            ChatDto(
                recipient=RecipientDto(id=IdFaker.fake().value, name='Recipient'),
                unread_messages_count=1,
            )
        )
        self.repository_mock.find_by_id_and_sender_id.return_value = chat

        result = self.use_case.execute(chat_id=chat.id.value, sender_id=sender_id)

        self.repository_mock.find_by_id_and_sender_id.assert_called_once_with(
            Id.create(chat.id.value),
            Id.create(sender_id),
        )
        assert result == chat.dto

    def test_should_raise_chat_not_found_error_when_chat_does_not_exist(self) -> None:
        chat_id = IdFaker.fake().value
        sender_id = IdFaker.fake().value
        self.repository_mock.find_by_id_and_sender_id.return_value = None

        with pytest.raises(ChatNotFoundError):
            self.use_case.execute(chat_id=chat_id, sender_id=sender_id)

        self.repository_mock.find_by_id_and_sender_id.assert_called_once_with(
            Id.create(chat_id),
            Id.create(sender_id),
        )
