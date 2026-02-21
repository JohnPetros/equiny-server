from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.use_cases import UpdateOwnerUseCase
from equiny.core.shared.domain.errors import NotFoundError
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.validation.profiling import OwnerSchema


class UpdateOwnerController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.put(
            '/',
            status_code=HTTPStatus.OK,
            response_model=OwnerDto,
        )
        def _(
            body: OwnerSchema,
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            repository: OwnersRepository = Depends(DatabasePipe.get_owners_repository),
        ) -> OwnerDto:
            owner = repository.find_by_id(owner_id)
            if owner is None:
                raise NotFoundError('Owner não encontrado')
            use_case = UpdateOwnerUseCase(repository)
            return use_case.execute(body.to_dto(owner))
