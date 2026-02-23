from typing import Annotated

from fastapi import Depends, Request

from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.matching.use_cases.verify_match_use_case import VerifyMatchUseCase
from equiny.core.conversation.domain.errors.chat_not_allowed_error import (
    ChatNotAllowedError,
)
from equiny.pipes.database_pipe import DatabasePipe

matches_repository = Annotated[
    MatchesRepository, Depends(DatabasePipe.get_matches_repository)
]


class MatchingPipe:
    @staticmethod
    async def verify_match(
        request: Request,
        repository: matches_repository,
    ) -> None:
        body = await request.json()
        use_case = VerifyMatchUseCase(repository)
        has_match = use_case.execute(
            body['recipient_horse_id'], body['sender_horse_id']
        )
        if not has_match:
            raise ChatNotAllowedError
