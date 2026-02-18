from datetime import datetime

from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.fakers.profiling.entities.horses_faker import HorsesFaker


class HorseMatchFaker:
    @staticmethod
    def fake(
        horse_id: str | None = None,
        created_at: datetime | None = None,
    ) -> HorseMatch:
        return HorseMatch.create(
            HorseMatchFaker.fake_dto(horse_id=horse_id, created_at=created_at)
        )

    @staticmethod
    def fake_dto(
        horse_id: str | None = None,
        created_at: datetime | None = None,
    ) -> HorseMatchDto:
        return HorseMatchDto(
            horse=HorsesFaker.fake_dto(id=horse_id),
            created_at=created_at or datetime.now(),
        )
