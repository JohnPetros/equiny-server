from unittest.mock import Mock, create_autospec

import pytest

from src.equiny.core.conversation.domain.entities.chat import Chat
from src.equiny.core.conversation.domain.entities.dtos.chat_dto import ChatDto
from src.equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto
from src.equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from src.equiny.core.conversation.use_cases.verify_chat_participant_use_case import (
    VerifyChatParticipantUseCase,
)
from src.equiny.core.shared.domain.structures.id import Id
from tests.fakers.shared.structures.id_faker import IdFaker


class TestVerifyChatParticipantUseCase:
    repository_mock: Mock
    use_case: VerifyChatParticipantUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(ChatsRepository, instance=True)
        self.use_case = VerifyChatParticipantUseCase(repository=self.repository_mock)

    def test_should_return_true_when_participant_belongs_to_chat(self) -> None:
        chat_id = IdFaker.fake().value
        participant_id = IdFaker.fake().value
        chat = Chat.create(
            ChatDto(
                recipient=RecipientDto(id=IdFaker.fake().value, name='Recipient'),
                unread_messages_count=0,
            )
        )
        self.repository_mock.find_by_id_and_participant_id.return_value = chat

        result = self.use_case.execute(chat_id=chat_id, participant_id=participant_id)

        self.repository_mock.find_by_id_and_participant_id.assert_called_once_with(
            chat_id=Id.create(chat_id),
            participant_id=Id.create(participant_id),
        )
        assert result is True

    def test_should_return_false_when_participant_does_not_belong_to_chat(self) -> None:
        chat_id = IdFaker.fake().value
        participant_id = IdFaker.fake().value
        self.repository_mock.find_by_id_and_participant_id.return_value = None

        result = self.use_case.execute(chat_id=chat_id, participant_id=participant_id)

        self.repository_mock.find_by_id_and_participant_id.assert_called_once_with(
            chat_id=Id.create(chat_id),
            participant_id=Id.create(participant_id),
        )
        assert result is False
