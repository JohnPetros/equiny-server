from equiny.core.profiling.domain.errors.horse_match_not_found_error import (
    HorseMatchNotFoundError,
)
from equiny.core.profiling.domain.events import HorseMatchNotifiedEvent
from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.interfaces import Broker


class NotifyHorseMatchUseCase:
    def __init__(self, repository: HorsesRepository, broker: Broker) -> None:
        self._repository = repository
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
        self._broker.publish(HorseMatchNotifiedEvent(horse_a_match.dto))
        self._broker.publish(HorseMatchNotifiedEvent(horse_b_match.dto))

    def _find_horse_match(self, from_horse_id: Id, to_horse_id: Id) -> HorseMatch:
        horse_match = self._repository.find_horse_match_by_horses(
            from_horse_id=from_horse_id,
            to_horse_id=to_horse_id,
        )
        if horse_match is None:
            raise HorseMatchNotFoundError

        return horse_match
