from unittest.mock import Mock, create_autospec

import pytest

from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases.list_chats_use_case import ListChatsUseCase
from equiny.core.shared.domain.structures.id import Id
from tests.fakers.shared.structures.id_faker import IdFaker


class TestListChatsUseCase:
    repository_mock: Mock
    use_case: ListChatsUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(ChatsRepository, instance=True)
        self.use_case = ListChatsUseCase(repository=self.repository_mock)

    def test_should_return_chat_dto_list_when_sender_has_chats(self) -> None:
        sender_id = IdFaker.fake().value
        first_chat = Chat.create(
            ChatDto(
                recipient=RecipientDto(id=IdFaker.fake().value, name='First Recipient'),
                unread_messages_count=0,
            )
        )
        second_chat = Chat.create(
            ChatDto(
                recipient=RecipientDto(
                    id=IdFaker.fake().value, name='Second Recipient'
                ),
                unread_messages_count=2,
            )
        )
        self.repository_mock.find_many_by_sender_id.return_value = [
            first_chat,
            second_chat,
        ]

        result = self.use_case.execute(sender_id=sender_id)

        self.repository_mock.find_many_by_sender_id.assert_called_once_with(
            Id.create(sender_id)
        )
        assert result == [first_chat.dto, second_chat.dto]

    def test_should_return_empty_list_when_sender_has_no_chats(self) -> None:
        sender_id = IdFaker.fake().value
        self.repository_mock.find_many_by_sender_id.return_value = []

        result = self.use_case.execute(sender_id=sender_id)

        self.repository_mock.find_many_by_sender_id.assert_called_once_with(
            Id.create(sender_id)
        )
        assert result == []
