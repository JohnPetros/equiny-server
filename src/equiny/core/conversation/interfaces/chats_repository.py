from typing import Protocol

from equiny.core.conversation.domain.entities.chat import Chat
from equiny.core.shared.domain.structures.id import Id


class ChatsRepository(Protocol):
    def add(self, chat: Chat, sender_id: Id) -> None: ...

    def find_many_by_sender_id(
        self,
        sender_id: Id,
    ) -> list[Chat]: ...

    def find_by_recipient_id_and_sender_id(
        self,
        recipient_id: Id,
        sender_id: Id,
    ) -> Chat | None: ...

    def find_by_id_and_participant_id(
        self,
        chat_id: Id,
        participant_id: Id,
    ) -> Chat | None: ...

    def find_by_id_and_sender_id(
        self,
        chat_id: Id,
        sender_id: Id,
    ) -> Chat | None: ...
