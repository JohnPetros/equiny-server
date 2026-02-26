from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.domain.errors.owner_not_found_error import OwnerNotFoundError
from equiny.core.profiling.domain.events import OwnerPresenceRegisteredEvent
from equiny.core.shared.interfaces.broker import Broker
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.interfaces.repositories import (
    HorsesRepository,
    OwnersRepository,
)
from equiny.constants import CACHE_KEYS


class RegisterOwnerPresenceUseCase:
    def __init__(
        self,
        cache_provider: CacheProvider,
        owners_repository: OwnersRepository,
        horses_repository: HorsesRepository,
        broker: Broker,
    ) -> None:
        self._cache_provider = cache_provider
        self._owners_repository = owners_repository
        self._horses_repository = horses_repository
        self._broker = broker

    def execute(self, owner_id: str) -> None:
        owner = self._find_owner(Id.create(owner_id))
        self._cache_provider.set(
            f'{CACHE_KEYS.OWNERS_PRESENCE}:{owner_id}', owner.id.value
        )
        owner_matches = self._find_owner_matches(owner.id)
        self._broker.publish(
            OwnerPresenceRegisteredEvent(
                owner.id.value,
                owner_matches,
            )
        )

    def _find_owner(self, owner_id: Id) -> Owner:
        owner = self._owners_repository.find_by_id(owner_id)
        if owner is None:
            raise OwnerNotFoundError
        return owner

    def _find_owner_matches(self, owner_id: Id) -> list[str]:
        horse_matches = self._horses_repository.find_horse_matches_by_owner_id(owner_id)
        return [match.owner_id.value for match in horse_matches]
