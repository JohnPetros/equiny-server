from equiny.constants import CACHE_KEYS
from equiny.core.profiling.domain.errors.owner_not_found_error import OwnerNotFoundError
from equiny.core.profiling.domain.structures import OwnerPresence
from equiny.core.profiling.domain.structures.dtos import OwnerPresenceDto
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.core.shared.domain.structures.id import Id


class GetOwnerPresenceUseCase:
    def __init__(
        self,
        cache_provider: CacheProvider,
        repository: OwnersRepository,
    ) -> None:
        self._cache_provider = cache_provider
        self._repository = repository

    def execute(self, owner_id: str) -> OwnerPresenceDto:
        owner = self._repository.find_by_id(Id.create(owner_id))
        if owner is None:
            raise OwnerNotFoundError

        cache_key = f'{CACHE_KEYS.OWNERS_PRESENCE}:{owner.id.value}'
        is_online = self._cache_provider.get(cache_key) is not None
        owner_presence = OwnerPresence.create(
            OwnerPresenceDto(
                owner_id=owner.id.value,
                is_online=is_online,
                last_seen_at=owner.last_presence_at.value
                if owner.last_presence_at is not None
                else None,
            )
        )
        return owner_presence.dto
