from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.shared.domain.structures.id import Id


class VerifyChatParticipantUseCase:
    def __init__(self, repository: ChatsRepository) -> None:
        self._repository = repository

    def execute(self, chat_id: str, participant_id: str) -> bool:
        chat = self._repository.find_by_id_and_participant_id(
            chat_id=Id.create(chat_id),
            participant_id=Id.create(participant_id),
        )
        return chat is not None
