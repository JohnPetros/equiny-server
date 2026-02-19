from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.matching.use_cases.dismatch_horse_use_case import DismatchHorseUseCase
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.validation.shared.id_schema import IdSchema


class DismatchHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.delete(
            '/',
            status_code=HTTPStatus.NO_CONTENT,
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            horse_a_id: Annotated[IdSchema, Query()],
            horse_b_id: Annotated[IdSchema, Query()],
            matches_repo: MatchesRepository = Depends(
                DatabasePipe.get_matches_repository
            ),
        ) -> None:
            use_case = DismatchHorseUseCase(matches_repo)
            use_case.execute(horse_a_id, horse_b_id)
