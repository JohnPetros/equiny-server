from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.structures.dtos import OwnerPresenceDto
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.use_cases import GetOwnerPresenceUseCase
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.providers_pipe import ProvidersPipe
from equiny.validation.shared.id_schema import IdSchema


class FetchOwnerPresenceController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/{owner_id}/presence',
            status_code=HTTPStatus.OK,
            response_model=OwnerPresenceDto,
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            owner_id: IdSchema,
            repository: OwnersRepository = Depends(DatabasePipe.get_owners_repository),
            cache_provider: CacheProvider = Depends(ProvidersPipe.get_cache_provider),
        ) -> OwnerPresenceDto:
            use_case = GetOwnerPresenceUseCase(
                cache_provider=cache_provider,
                repository=repository,
            )
            return use_case.execute(owner_id)
