from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.domain.errors.owner_not_found_error import OwnerNotFoundError
from equiny.core.profiling.domain.events import OwnerPresenceRegisteredEvent
from equiny.core.shared.interfaces.broker import Broker
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.constants import CACHE_KEYS


class RegisterOwnerPresenceUseCase:
    def __init__(
        self,
        cache_provider: CacheProvider,
        repository: OwnersRepository,
        broker: Broker,
    ) -> None:
        self._cache_provider = cache_provider
        self._repository = repository
        self._broker = broker

    def execute(self, owner_id: str) -> None:
        owner = self._find_owner(Id.create(owner_id))
        self._cache_provider.set(
            f'{CACHE_KEYS.OWNERS_PRESENCE}:{owner_id}', owner.id.value
        )
        self._broker.publish(OwnerPresenceRegisteredEvent(owner_id))

    def _find_owner(self, owner_id: Id) -> Owner:
        owner = self._repository.find_by_id(owner_id)
        if owner is None:
            raise OwnerNotFoundError
        return owner
