from typing import Union

from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.id import Id
from equiny.core.matching.domain.structures.match import Match
from equiny.core.shared.domain.structures.datetime import Datetime
from equiny.core.matching.domain.structures.dtos.swipe_dto import SwipeDto
from equiny.core.matching.domain.structures.swipe_decision import SwipeDecision
from equiny.core.matching.domain.structures.dtos.match_dto import MatchDto


@structure
class Swipe(Structure):
    from_horse_id: Id
    to_horse_id: Id
    decision: SwipeDecision
    created_at: Datetime

    @classmethod
    def create(cls, dto: SwipeDto) -> 'Swipe':
        return Swipe(
            from_horse_id=Id.create(dto.from_horse_id),
            to_horse_id=Id.create(dto.to_horse_id),
            decision=SwipeDecision.create(dto.decision),
            created_at=Datetime.create(dto.created_at),
        )

    def verify_match(self, other_swipe: 'Swipe') -> Union['Match', None]:
        if (
            self.from_horse_id == other_swipe.to_horse_id
            and self.to_horse_id == other_swipe.from_horse_id
            and self.decision.is_like().is_true
            and other_swipe.decision.is_like().is_true
        ):
            return Match.create(
                MatchDto(
                    horse_a_id=self.from_horse_id.value,
                    horse_b_id=self.to_horse_id.value,
                    created_at=self.created_at.value,
                )
            )

        return None

    @property
    def dto(self) -> SwipeDto:
        return SwipeDto(
            from_horse_id=self.from_horse_id.value,
            to_horse_id=self.to_horse_id.value,
            created_at=self.created_at.value,
            decision=self.decision.value,
        )
