from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.matching.domain.errors import MatchNotFoundError
from equiny.core.shared.domain.structures.id import Id


class DismatchHorseUseCase:
    def __init__(self, matches_repository: MatchesRepository) -> None:
        self._matches_repository = matches_repository

    def execute(self, horse_a_id: str, horse_b_id: str) -> None:
        match = self._matches_repository.find_by_horses(
            Id.create(horse_a_id), Id.create(horse_b_id)
        )

        if match is None:
            raise MatchNotFoundError

        self._matches_repository.remove(match)
