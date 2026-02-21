from equiny.core.shared.domain.structures.id import Id
from equiny.core.matching.interfaces.matches_repository import MatchesRepository


class VerifyMatchUseCase:
    def __init__(self, repository: MatchesRepository) -> None:
        self._repository = repository

    def execute(self, horse_a_id: str, horse_b_id: str) -> bool:
        match = self._repository.find_by_horses(
            Id.create(horse_a_id), Id.create(horse_b_id)
        )
        return match is not None
