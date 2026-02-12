from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.use_cases.get_horse_use_case import GetHorseUseCase
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.pipes import DatabasePipe


class FetchHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/{horse_id}',
            status_code=HTTPStatus.OK,
            response_model=HorseDto,
        )
        async def _(
            horse_id: str,
            repository: HorsesRepository = Depends(DatabasePipe.get_horses_repository),
        ) -> HorseDto:
            use_case = GetHorseUseCase(repository)
            return use_case.execute(horse_id)
