from equiny.core.matching.domain.structures.match import Match
from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.responses.pagination_response import PaginationResponse
from equiny.database.sqlalchemy.mappers.matching.matches_mapper import MatchesMapper
from equiny.database.sqlalchemy.models.matching.match_model import MatchModel
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)


class SqlalchemyMatchesRepository(SqlalchemyRepository, MatchesRepository):
    def add(self, match: Match) -> None:
        model = MatchesMapper.to_model(match)
        self.sqlalchemy.add(model)

    def find_many_by_horse(self, horse_id: Id) -> PaginationResponse[Match]:
        models = (
            self.sqlalchemy.query(MatchModel)
            .filter(
                (MatchModel.horse_a_id == horse_id.value)
                | (MatchModel.horse_b_id == horse_id.value)
            )
            .all()
        )
        matches = [MatchesMapper.to_entity(model) for model in models]
        return PaginationResponse(items=matches, next_cursor=None, has_more=False)

    def find_by_horses(self, horse_a_id: Id, horse_b_id: Id) -> Match | None:
        model = (
            self.sqlalchemy.query(MatchModel)
            .filter(
                (
                    (MatchModel.horse_a_id == horse_a_id.value)
                    & (MatchModel.horse_b_id == horse_b_id.value)
                )
                | (
                    (MatchModel.horse_a_id == horse_b_id.value)
                    & (MatchModel.horse_b_id == horse_a_id.value)
                )
            )
            .first()
        )
        if model is None:
            return None
        return MatchesMapper.to_entity(model)

    def remove(self, match: Match) -> None:
        self.sqlalchemy.query(MatchModel).filter(
            MatchModel.id == match.horse_a_id.value
        ).delete()
