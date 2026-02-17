from equiny.core.matching.domain.structures.dtos.swipe_dto import SwipeDto
from equiny.core.matching.domain.structures.swipe import Swipe
from equiny.core.matching.interfaces import SwipesRepository, MatchesRepository


class SwipeHorseUseCase:
    def __init__(
        self, swipes_repository: SwipesRepository, matches_repository: MatchesRepository
    ) -> None:
        self._swipes_repository = swipes_repository
        self._matches_repository = matches_repository

    def execute(self, dto: SwipeDto) -> SwipeDto:
        from equiny.core.matching.domain.errors.swipe_already_registered_error import (
            SwipeAlreadyRegisteredError,
        )

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

        self._swipes_repository.add(swipe)
        return swipe.dto
