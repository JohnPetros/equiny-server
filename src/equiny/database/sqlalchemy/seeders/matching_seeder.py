from typing import TYPE_CHECKING

from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.fakers.matching.structures import MatchFaker

if TYPE_CHECKING:
    from equiny.core.matching.domain.structures.match import Match


class MatchingSeeder:
    def __init__(self, matches_repository: MatchesRepository) -> None:
        self._matches_repository = matches_repository

    def seed(self, horses_ids: list[Id]) -> None:
        first_horse_id = horses_ids[0]
        other_horses_ids = horses_ids[1:]
        matches: list[Match] = []
        for other_horse_id in other_horses_ids:
            match = MatchFaker.fake(
                horse_a_id=first_horse_id.value,
                horse_b_id=other_horse_id.value,
            )
            matches.append(match)
        self._matches_repository.add_many(matches)
