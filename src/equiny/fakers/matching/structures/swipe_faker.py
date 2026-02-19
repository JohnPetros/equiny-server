from datetime import datetime
from faker import Faker

from equiny.core.matching.domain.structures.dtos.swipe_dto import SwipeDto
from equiny.core.matching.domain.structures.swipe import Swipe
from equiny.core.matching.domain.structures.swipe_decision import SwipeDecisionValue
from equiny.fakers.shared.structures.id_faker import IdFaker


class SwipeFaker:
    _faker = Faker()

    @staticmethod
    def fake(
        from_horse_id: str | None = None,
        to_horse_id: str | None = None,
        decision: SwipeDecisionValue | None = None,
        created_at: datetime | None = None,
        is_match: bool = False,
    ) -> Swipe:
        return Swipe.create(
            SwipeFaker.fake_dto(
                from_horse_id=from_horse_id,
                to_horse_id=to_horse_id,
                decision=decision,
                created_at=created_at,
                is_match=is_match,
            )
        )

    @staticmethod
    def fake_dto(
        from_horse_id: str | None = None,
        to_horse_id: str | None = None,
        decision: SwipeDecisionValue | None = None,
        created_at: datetime | None = None,
        is_match: bool = False,
    ) -> SwipeDto:
        return SwipeDto(
            from_horse_id=from_horse_id or IdFaker.fake().value,
            to_horse_id=to_horse_id or IdFaker.fake().value,
            decision=decision or SwipeDecisionValue.LIKE,
            created_at=created_at or datetime.now(),
            is_match=is_match,
        )
