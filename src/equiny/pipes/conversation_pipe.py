from typing import Annotated

from fastapi import Depends
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.use_cases import VerifyChatParticipantUseCase
from equiny.core.conversation.domain.errors.chat_not_allowed_error import (
    ChatNotAllowedError,
)
from equiny.database.sqlalchemy.repositories.conversation.sqlalchemy_chats_repository import (
    SqlalchemyChatsRepository,
)
from equiny.database.sqlalchemy.sqlalchemy import Sqlalchemy
from equiny.pipes.database_pipe import DatabasePipe
from equiny.core.shared.domain.structures.id import Id

repository = Annotated[ChatsRepository, Depends(DatabasePipe.get_chats_repository)]


class ConversationPipe:
    @staticmethod
    async def verify_chat_participant(
        chat_id: str,
        owner_id: str,
        sqlalchemy: Sqlalchemy = Depends(DatabasePipe.get_sqlalchemy),
    ) -> Id:
        with sqlalchemy.session() as sqlalchemy_session:
            chats_repository = SqlalchemyChatsRepository(sqlalchemy_session)
            use_case = VerifyChatParticipantUseCase(chats_repository)
            has_chat = use_case.execute(chat_id=chat_id, participant_id=owner_id)
            if not has_chat:
                raise ChatNotAllowedError
            return Id.create(owner_id)
