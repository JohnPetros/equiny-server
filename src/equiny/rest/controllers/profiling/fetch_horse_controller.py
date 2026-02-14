from http import HTTPStatus
from fastapi import APIRouter, Depends
from typing import Annotated

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.use_cases.get_horse_use_case import GetHorseUseCase
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.pipes import DatabasePipe
from equiny.pipes.auth_pipe import AuthPipe


repository = Annotated[HorsesRepository, Depends(DatabasePipe.get_horses_repository)]


class FetchHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/{horse_id}',
            status_code=HTTPStatus.OK,
            response_model=HorseDto,
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            horse_id: str,
            repository: repository,
        ) -> HorseDto:
            use_case = GetHorseUseCase(repository)
            return use_case.execute(horse_id)
