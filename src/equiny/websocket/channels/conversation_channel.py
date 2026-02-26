from typing import Any

from equiny.core.conversation.domain.entities.dtos.chat_message_dto import MessageDto
from equiny.core.conversation.domain.events import (
    MessageSentEvent,
)
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.interfaces.messages_repository import MessagesRepository
from equiny.core.conversation.use_cases.send_message_use_case import SendMessageUseCase
from equiny.core.shared.domain.errors.app_error import AppError
from equiny.core.shared.interfaces.broker import Broker
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.validation.shared.id_schema import IdSchema
from equiny.validation.shared.schema import Schema


class ConversationChannel:
    def __init__(
        self,
        broker: Broker,
        chats_repository: ChatsRepository,
        messages_repository: MessagesRepository,
        cache_provider: CacheProvider,
    ) -> None:
        self._broker = broker
        self._chats_repository = chats_repository
        self._messages_repository = messages_repository
        self._cache_provider = cache_provider

    def handle(self, event_name: str, event_payload: Any) -> None:
        print(f'Event name: {event_name}')
        match event_name:
            case MessageSentEvent.name:
                self._on_message_sent(event_payload)
            case _:
                raise AppError('WebSocket Error', f'Event {event_name} not supported')

    def _on_message_sent(self, event_payload: Any) -> None:
        class PayloadSchema(Schema):
            message_content: str
            chat_id: IdSchema
            sender_id: IdSchema

        payload = PayloadSchema.model_validate(event_payload)

        use_case = SendMessageUseCase(
            self._chats_repository,
            self._messages_repository,
            self._cache_provider,
            self._broker,
        )
        use_case.execute(
            MessageDto(
                content=payload.message_content,
                sender_id=payload.sender_id,
                attachments=[],
            ),
            payload.chat_id,
        )
