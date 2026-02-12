from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.pipes.auth_pipe import AuthPipe
from equiny.validation.profiling import HorseSchema
from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.use_cases import CreateHorseUseCase
from equiny.pipes.database_pipe import DatabasePipe


class CreateHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/',
            status_code=HTTPStatus.CREATED,
            response_model=HorseDto,
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        async def _(
            body: HorseSchema,
            repository: HorsesRepository = Depends(DatabasePipe.get_horses_repository),
        ) -> HorseDto:
            use_case = CreateHorseUseCase(repository)
            return use_case.execute(body.to_dto())
