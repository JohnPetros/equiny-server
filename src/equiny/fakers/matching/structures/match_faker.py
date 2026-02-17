from datetime import datetime
from faker import Faker

from equiny.core.matching.domain.structures.dtos.match_dto import MatchDto
from equiny.core.matching.domain.structures.match import Match
from equiny.fakers.shared.structures.id_faker import IdFaker


class MatchFaker:
    _faker = Faker()

    @staticmethod
    def fake(
        horse_a_id: str | None = None,
        horse_b_id: str | None = None,
        created_at: datetime | None = None,
    ) -> Match:
        return Match.create(
            MatchFaker.fake_dto(
                horse_a_id=horse_a_id,
                horse_b_id=horse_b_id,
                created_at=created_at,
            )
        )

    @staticmethod
    def fake_dto(
        horse_a_id: str | None = None,
        horse_b_id: str | None = None,
        created_at: datetime | None = None,
    ) -> MatchDto:
        return MatchDto(
            horse_a_id=horse_a_id or IdFaker.fake().value,
            horse_b_id=horse_b_id or IdFaker.fake().value,
            created_at=created_at or datetime.now(),
        )
