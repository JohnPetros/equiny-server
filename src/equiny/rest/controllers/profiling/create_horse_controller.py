from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends

from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.validation.profiling import HorseSchema
from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.use_cases import CreateHorseUseCase
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe


repository = Annotated[HorsesRepository, Depends(DatabasePipe.get_horses_repository)]


class CreateHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/',
            status_code=HTTPStatus.CREATED,
            response_model=HorseDto,
        )
        def _(
            body: HorseSchema,
            owner: Owner = Depends(ProfilingPipe.get_owner),
            repository: HorsesRepository = Depends(DatabasePipe.get_horses_repository),
        ) -> HorseDto:
            use_case = CreateHorseUseCase(repository)
            return use_case.execute(body.to_dto(), owner.id.value)
