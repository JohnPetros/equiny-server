from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases import ToggleHorseActivationUseCase
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe


class ToggleHorseActivationController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.patch(
            '/{horse_id}/activation',
            status_code=HTTPStatus.OK,
            response_model=HorseDto,
        )
        def _(
            horse_id: str,
            owner: Owner = Depends(ProfilingPipe.get_owner),
            repository: HorsesRepository = Depends(DatabasePipe.get_horses_repository),
        ) -> HorseDto:
            use_case = ToggleHorseActivationUseCase(repository)
            return use_case.execute(horse_id, owner.id.value)
