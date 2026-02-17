from equiny.core.matching.domain.structures.dtos.match_dto import MatchDto
from equiny.core.matching.domain.structures.match import Match
from equiny.database.sqlalchemy.models.matching.match_model import MatchModel


class MatchesMapper:
    @staticmethod
    def to_entity(model: MatchModel) -> Match:
        dto = MatchDto(
            horse_a_id=model.horse_a_id,
            horse_b_id=model.horse_b_id,
            created_at=model.created_at,
        )
        return Match.create(dto)

    @staticmethod
    def to_model(match: Match) -> MatchModel:
        dto = match.dto
        return MatchModel(
            horse_a_id=dto.horse_a_id,
            horse_b_id=dto.horse_b_id,
        )
