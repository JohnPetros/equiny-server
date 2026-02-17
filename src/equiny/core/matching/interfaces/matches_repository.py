from typing import Protocol

from equiny.core.matching.domain.structures.match import Match
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.responses.pagination_response import PaginationResponse


class MatchesRepository(Protocol):
    def add(self, match: Match) -> None: ...

    def find_many_by_horse(self, horse_id: Id) -> PaginationResponse[Match]: ...

    def find_by_horses(self, horse_a_id: Id, horse_b_id: Id) -> Match | None: ...

    def remove(self, match: Match) -> None: ...
