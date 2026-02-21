from typing import Annotated

from fastapi import Depends
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases import VerifyChatParticipantUseCase
from equiny.core.conversation.domain.errors.chat_not_allowed_error import (
    ChatNotAllowedError,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.pipes.database_pipe import DatabasePipe

repository = Annotated[ChatsRepository, Depends(DatabasePipe.get_chats_repository)]


class ConversationPipe:
    @staticmethod
    async def verify_chat_participant(
        chat_id: str,
        owner_id: Id = Depends(ProfilingPipe.get_owner_id),
        chats_repository: ChatsRepository = Depends(DatabasePipe.get_chats_repository),
    ) -> None:
        use_case = VerifyChatParticipantUseCase(chats_repository)
        has_chat = use_case.execute(chat_id=chat_id, participant_id=owner_id.value)
        if not has_chat:
            raise ChatNotAllowedError
