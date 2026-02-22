from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.conversation.domain.entities.dtos import ChatDto
from equiny.core.shared.responses.list_response import ListResponse


class ListChatsUseCase:
    def __init__(self, repository: ChatsRepository) -> None:
        self._repository = repository

    def execute(self, sender_id: str) -> ListResponse[ChatDto]:
        chats = self._repository.find_many_by_sender_id(Id.create(sender_id))
        return ListResponse[ChatDto](items=[chat.dto for chat in chats])
