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

    def add_many(self, matches: list[Match]) -> None:
        models = [MatchesMapper.to_model(match) for match in matches]
        self.sqlalchemy.add_all(models)

    def find_many_by_horse(
        self, horse_id: Id, cursor: str | None = None, limit: int = 20
    ) -> PaginationResponse[Match]:
        query = self.sqlalchemy.query(MatchModel).filter(
            (MatchModel.horse_a_id == horse_id.value)
            | (MatchModel.horse_b_id == horse_id.value)
        )

        if cursor:
            query = query.filter(MatchModel.created_at < cursor)

        models = query.order_by(MatchModel.created_at.desc()).limit(limit + 1).all()

        has_more = len(models) > limit
        if has_more:
            models = models[:limit]

        matches = [MatchesMapper.to_entity(model) for model in models]
        next_cursor = matches[-1].created_at.value.isoformat() if has_more else None

        return PaginationResponse(
            items=matches, next_cursor=next_cursor, has_more=has_more
        )

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
            (
                (MatchModel.horse_a_id == match.horse_a_id.value)
                & (MatchModel.horse_b_id == match.horse_b_id.value)
            )
            | (
                (MatchModel.horse_a_id == match.horse_b_id.value)
                & (MatchModel.horse_b_id == match.horse_a_id.value)
            )
        ).delete()
