from typing import Protocol

from equiny.core.conversation.domain.entities.message import Message
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.integer import Integer
from equiny.core.shared.responses.pagination_response import PaginationResponse


class MessagesRepository(Protocol):
    def add(self, message: Message, chat_id: Id) -> None: ...

    def find_by_chat_id_and_sender_id(
        self,
        chat_id: Id,
        sender_id: Id,
    ) -> Message: ...

    def find_many_by_chat_id_and_sender_id(
        self,
        chat_id: Id,
        sender_id: Id,
        cursor: Id | None,
        limit: Integer,
    ) -> PaginationResponse[Message]: ...

    def mark_viewed_by_recipient(self, chat_id: Id, recipient_id: Id) -> None: ...
