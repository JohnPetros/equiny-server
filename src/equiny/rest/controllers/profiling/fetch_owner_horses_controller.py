from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases import GetOwnerHorsesUseCase
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe


class FetchOwnerHorsesController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/me/horses',
            status_code=HTTPStatus.OK,
            response_model=list[HorseDto],
        )
        def _(
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            repository: HorsesRepository = Depends(DatabasePipe.get_horses_repository),
        ) -> list[HorseDto]:
            use_case = GetOwnerHorsesUseCase(repository)
            return use_case.execute(owner_id.value)
