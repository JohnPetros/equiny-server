from equiny.core.matching.domain.structures.dtos.swipe_dto import SwipeDto
from equiny.core.matching.domain.structures.swipe import Swipe
from equiny.core.matching.interfaces import SwipesRepository, MatchesRepository
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.notify_horse_match_use_case import (
    NotifyHorseMatchUseCase,
)
from equiny.core.shared.interfaces.broker import Broker
from equiny.core.matching.domain.errors.swipe_already_registered_error import (
    SwipeAlreadyRegisteredError,
)


class SwipeHorseUseCase:
    def __init__(
        self,
        swipes_repository: SwipesRepository,
        matches_repository: MatchesRepository,
        horses_repository: HorsesRepository,
        broker: Broker,
    ) -> None:
        self._swipes_repository = swipes_repository
        self._matches_repository = matches_repository
        self._horses_repository = horses_repository
        self._broker = broker

    def execute(self, dto: SwipeDto) -> SwipeDto:
        swipe = Swipe.create(dto)

        existing = self._swipes_repository.find_by_horses(
            swipe.from_horse_id, swipe.to_horse_id
        )
        if existing is not None:
            raise SwipeAlreadyRegisteredError

        reverse_swipe = self._swipes_repository.find_by_horses(
            swipe.to_horse_id, swipe.from_horse_id
        )
        if reverse_swipe is not None:
            match = swipe.verify_match(reverse_swipe)
            if match is not None:
                self._matches_repository.add(match)
                NotifyHorseMatchUseCase(self._horses_repository, self._broker).execute(
                    match.horse_a_id.value,
                    match.horse_b_id.value,
                )
                swipe = swipe.become_match()

        self._swipes_repository.add(swipe)
        return swipe.dto
