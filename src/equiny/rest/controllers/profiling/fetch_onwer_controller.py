from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.entities.dtos.owner_dto import OwnerDto
from equiny.core.profiling.use_cases import GetOwnerUseCase
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.shared.domain.structures.id import Id


class FetchOwnerController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/me',
            status_code=HTTPStatus.OK,
            response_model=OwnerDto,
        )
        def _(
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            repository: OwnersRepository = Depends(DatabasePipe.get_owners_repository),
        ) -> OwnerDto:
            use_case = GetOwnerUseCase(repository)
            return use_case.execute(owner_id.value)
