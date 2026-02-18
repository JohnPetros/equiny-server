from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.interfaces.repositories import HorsesRepository


class ListHorseMatchesUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self._repository = repository

    def execute(self, horse_id: str) -> list[HorseMatch]:
        matches = self._repository.find_all_matches(Id.create(horse_id))
        return [HorseMatch.create(match.dto) for match in matches]
