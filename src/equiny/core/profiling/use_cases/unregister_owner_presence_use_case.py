from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.domain.errors.owner_not_found_error import OwnerNotFoundError
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.constants import CACHE_KEYS


class UnregisterOwnerPresenceUseCase:
    def __init__(
        self, cache_provider: CacheProvider, repository: OwnersRepository
    ) -> None:
        self._cache_provider = cache_provider
        self._repository = repository

    def execute(self, owner_id: str) -> None:
        self._cache_provider.delete(f'{CACHE_KEYS.OWNERS_PRESENCE}:{owner_id}')
        owner = self._find_owner(Id.create(owner_id))
        owner.leave_presence()
        self._repository.replace(owner)

    def _find_owner(self, owner_id: Id) -> Owner:
        owner = self._repository.find_by_id(owner_id)
        if owner is None:
            raise OwnerNotFoundError
        return owner
