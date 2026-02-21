from typing import Annotated

from fastapi import Request
from fastapi import Depends
from sqlalchemy.orm import Session

from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.matching.interfaces.swipes_repository import SwipesRepository
from equiny.core.conversation.interfaces.chats_repository import ChatsRepository
from equiny.core.conversation.interfaces.messages_repository import (
    MessagesRepository,
)
from equiny.database.sqlalchemy.repositories.auth import SqlalchemyAccountsRepository
from equiny.core.profiling.interfaces.repositories import (
    HorsesRepository,
    OwnersRepository,
)
from equiny.database.sqlalchemy.repositories.matching import (
    SqlalchemyMatchesRepository,
    SqlalchemySwipesRepository,
)
from equiny.database.sqlalchemy.repositories.conversation import (
    SqlalchemyChatsRepository,
    SqlalchemyMessagesRepository,
)
from equiny.database.sqlalchemy.repositories.profiling import (
    SqlalchemyHorsesRepository,
    SqlalchemyOwnersRepository,
)


def get_sqlalchemy_session(request: Request) -> Session:
    return request.state.sqlalchemy_session


class DatabasePipe:
    @staticmethod
    def get_horses_repository(
        sqlalchemy: Annotated[Session, Depends(get_sqlalchemy_session)],
    ) -> HorsesRepository:
        return SqlalchemyHorsesRepository(sqlalchemy)

    @staticmethod
    def get_owners_repository(
        sqlalchemy: Annotated[Session, Depends(get_sqlalchemy_session)],
    ) -> OwnersRepository:
        return SqlalchemyOwnersRepository(sqlalchemy)

    @staticmethod
    def get_accounts_repository(
        sqlalchemy: Annotated[Session, Depends(get_sqlalchemy_session)],
    ) -> AccountsRepository:
        return SqlalchemyAccountsRepository(sqlalchemy)

    @staticmethod
    def get_swipes_repository(
        sqlalchemy: Annotated[Session, Depends(get_sqlalchemy_session)],
    ) -> SwipesRepository:
        return SqlalchemySwipesRepository(sqlalchemy)

    @staticmethod
    def get_matches_repository(
        sqlalchemy: Annotated[Session, Depends(get_sqlalchemy_session)],
    ) -> MatchesRepository:
        return SqlalchemyMatchesRepository(sqlalchemy)

    @staticmethod
    def get_chats_repository(
        sqlalchemy: Annotated[Session, Depends(get_sqlalchemy_session)],
    ) -> ChatsRepository:
        return SqlalchemyChatsRepository(sqlalchemy)

    @staticmethod
    def get_messages_repository(
        sqlalchemy: Annotated[Session, Depends(get_sqlalchemy_session)],
    ) -> MessagesRepository:
        return SqlalchemyMessagesRepository(sqlalchemy)
