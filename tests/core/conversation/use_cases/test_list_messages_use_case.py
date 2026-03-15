import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from equiny.core.conversation.domain.entities.dtos.chat_message_dto import (
    MessageDto,
)
from equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto
from equiny.core.conversation.domain.entities.message import Message
from equiny.core.conversation.domain.errors.chat_not_found_error import (
    ChatNotFoundError,
)
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.interfaces.messages_repository import (
    MessagesRepository,
)
from equiny.core.conversation.use_cases.list_messages_use_case import (
    ListMessagesUseCase,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.responses.pagination_response import PaginationResponse
from tests.fakers.shared.structures.id_faker import IdFaker


class TestListMessagesUseCase:
    chats_repository_mock: Mock
    messages_repository_mock: Mock
    use_case: ListMessagesUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.chats_repository_mock = create_autospec(ChatsRepository, instance=True)
        self.messages_repository_mock = create_autospec(
            MessagesRepository,
            instance=True,
        )
        self.use_case = ListMessagesUseCase(
            chats_repository=self.chats_repository_mock,
            messages_repository=self.messages_repository_mock,
        )

    def test_should_return_pagination_with_message_dtos_when_chat_exists(self) -> None:
        sender_id = IdFaker.fake().value
        cursor = IdFaker.fake().value
        chat = Chat.create(
            ChatDto(
                recipient=RecipientDto(id=IdFaker.fake().value, name='Recipient'),
                unread_messages_count=3,
            )
        )
        message = Message.create(
            MessageDto(
                sender_id=sender_id,
                content='hello',
                attachments=[],
            )
        )
        pagination = PaginationResponse(
            items=[message],
            next_cursor=message.id.value,
            has_more=True,
        )
        self.chats_repository_mock.find_by_id_and_sender_id.return_value = chat
        self.messages_repository_mock.find_many_by_chat_id_and_sender_id.return_value = pagination

        result = self.use_case.execute(
            chat_id=chat.id.value,
            sender_id=sender_id,
            cursor=cursor,
            limit=10,
        )

        self.chats_repository_mock.find_by_id_and_sender_id.assert_called_once_with(
            Id.create(chat.id.value),
            Id.create(sender_id),
        )
        self.messages_repository_mock.mark_read_by_recipient.assert_called_once_with(
            chat.id,
            Id.create(sender_id),
        )
        self.messages_repository_mock.find_many_by_chat_id_and_sender_id.assert_called_once()
        call_args = self.messages_repository_mock.find_many_by_chat_id_and_sender_id.call_args.args
        assert call_args[0] == chat.id
        assert call_args[1] == Id.create(sender_id)
        assert call_args[2] == Id.create(cursor)
        assert call_args[3].value == 10
        assert result.items == [message.dto]
        assert result.next_cursor == message.id.value
        assert result.has_more is True

    def test_should_raise_chat_not_found_error_when_chat_does_not_exist(self) -> None:
        chat_id = IdFaker.fake().value
        sender_id = IdFaker.fake().value
        self.chats_repository_mock.find_by_id_and_sender_id.return_value = None

        with pytest.raises(ChatNotFoundError):
            self.use_case.execute(chat_id=chat_id, sender_id=sender_id)

        self.messages_repository_mock.mark_read_by_recipient.assert_not_called()
        self.messages_repository_mock.find_many_by_chat_id_and_sender_id.assert_not_called()
