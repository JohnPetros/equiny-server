from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.domain.errors import (
    HorseMatchNotFoundError,
    OwnerNotFoundError,
)
from equiny.core.profiling.domain.events import HorseMatchNotifiedEvent
from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.core.profiling.interfaces.repositories import (
    HorsesRepository,
    OwnersRepository,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.interfaces import Broker


class NotifyHorseMatchUseCase:
    def __init__(
        self,
        horses_repository: HorsesRepository,
        owners_repository: OwnersRepository,
        broker: Broker,
    ) -> None:
        self._horses_repository = horses_repository
        self._owners_repository = owners_repository
        self._broker = broker

    def execute(
        self,
        horse_a_id: str,
        horse_b_id: str,
    ) -> None:
        horse_a_match = self._find_horse_match(
            Id.create(horse_a_id),
            Id.create(horse_b_id),
        )
        horse_b_match = self._find_horse_match(
            Id.create(horse_b_id),
            Id.create(horse_a_id),
        )
        horse_a_owner = self._find_horse_owner(horse_a_match.owner_id)
        horse_b_owner = self._find_horse_owner(horse_b_match.owner_id)
        self._broker.publish(
            HorseMatchNotifiedEvent(horse_a_match.dto, horse_b_owner.id.value)
        )
        self._broker.publish(
            HorseMatchNotifiedEvent(horse_b_match.dto, horse_a_owner.id.value)
        )

    def _find_horse_match(self, from_horse_id: Id, to_horse_id: Id) -> HorseMatch:
        horse_match = self._horses_repository.find_horse_match_by_horses(
            from_horse_id=from_horse_id,
            to_horse_id=to_horse_id,
        )
        if horse_match is None:
            raise HorseMatchNotFoundError

        return horse_match

    def _find_horse_owner(self, owner_id: Id) -> Owner:
        owner = self._owners_repository.find_by_id(owner_id)
        if owner is None:
            raise OwnerNotFoundError
        return owner
