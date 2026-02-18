from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.list_horse_matches_use_case import (
    ListHorseMatchesUseCase,
)
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.validation.shared import IdSchema


repository = Annotated[HorsesRepository, Depends(DatabasePipe.get_horses_repository)]


class ListHorseMatchesController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/{horse_id}/matches',
            status_code=HTTPStatus.OK,
            response_model=list[HorseMatchDto],
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            horse_id: IdSchema,
            repository: repository,
        ) -> list[HorseMatchDto]:
            use_case = ListHorseMatchesUseCase(repository)
            matches = use_case.execute(horse_id)
            return [match.dto for match in matches]
