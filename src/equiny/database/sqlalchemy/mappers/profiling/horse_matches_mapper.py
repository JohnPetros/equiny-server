from datetime import datetime

from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.database.sqlalchemy.mappers.profiling.horses_mapper import HorsesMapper
from equiny.database.sqlalchemy.models.profiling.horse_model import HorseModel


class HorseMatchesMapper:
    @staticmethod
    def to_entity(horse_model: HorseModel, created_at: datetime) -> HorseMatch:
        return HorseMatch.create(
            HorseMatchDto(
                horse=HorsesMapper.to_dto(horse_model),
                created_at=created_at,
            )
        )
