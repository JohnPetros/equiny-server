from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases import UpdateHorseUseCase
from equiny.core.shared.domain.structures.id import Id
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.validation.profiling import HorseSchema


class UpdateHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.put(
            '/{horse_id}',
            status_code=HTTPStatus.OK,
            response_model=HorseDto,
        )
        def _(
            horse_id: str,
            body: HorseSchema,
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            repository: HorsesRepository = Depends(DatabasePipe.get_horses_repository),
        ) -> HorseDto:
            use_case = UpdateHorseUseCase(repository)
            return use_case.execute(horse_id, owner_id.value, body.to_dto())
