import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto
from equiny.core.conversation.domain.errors.chat_already_exists_error import (
    ChatAlreadyExistsError,
)
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases.create_chat_use_case import CreateChatUseCase
from equiny.core.shared.domain.structures.id import Id
from tests.fakers.shared.structures.id_faker import IdFaker


class TestCreateChatUseCase:
    repository_mock: Mock
    use_case: CreateChatUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(ChatsRepository, instance=True)
        self.repository_mock.find_by_recipient_id_and_sender_id.return_value = None
        self.use_case = CreateChatUseCase(chats_repository=self.repository_mock)

    def test_should_create_chat_and_add_it_to_repository(self) -> None:
        recipient_id = IdFaker.fake().value
        sender_id = IdFaker.fake().value

        result = self.use_case.execute(recipient_id=recipient_id, sender_id=sender_id)

        self.repository_mock.find_by_recipient_id_and_sender_id.assert_called_once_with(
            recipient_id=Id.create(recipient_id),
            sender_id=Id.create(sender_id),
        )
        self.repository_mock.add.assert_called_once()
        added_chat, added_sender_id = self.repository_mock.add.call_args.args
        assert added_sender_id == Id.create(sender_id)
        assert result == added_chat.dto
        assert result.recipient.id == recipient_id
        assert result.unread_messages_count == 0

    def test_should_raise_chat_already_exists_error_when_chat_exists(self) -> None:
        recipient_id = IdFaker.fake().value
        sender_id = IdFaker.fake().value
        existing_chat = Chat.create(
            ChatDto(
                recipient=RecipientDto(id=recipient_id, name='Recipient'),
                unread_messages_count=0,
            )
        )
        self.repository_mock.find_by_recipient_id_and_sender_id.return_value = (
            existing_chat
        )

        with pytest.raises(ChatAlreadyExistsError):
            self.use_case.execute(recipient_id=recipient_id, sender_id=sender_id)

        self.repository_mock.add.assert_not_called()
