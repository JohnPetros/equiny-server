from equiny.core.matching.domain.structures.dtos.match_dto import MatchDto
from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.responses.pagination_response import PaginationResponse


class ListMatchesUseCase:
    def __init__(self, matches_repository: MatchesRepository) -> None:
        self._repository = matches_repository

    def execute(
        self, horse_id: str, cursor: str | None = None, limit: int = 20
    ) -> PaginationResponse[MatchDto]:
        pagination_response = self._repository.find_many_by_horse(
            Id.create(horse_id), cursor, limit
        )
        return pagination_response.map_items(lambda match: match.dto)
