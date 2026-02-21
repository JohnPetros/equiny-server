from datetime import datetime

from pydantic import BaseModel

from equiny.core.matching.domain.structures.dtos.swipe_dto import SwipeDto
from equiny.core.matching.domain.structures.swipe_decision import SwipeDecisionValue


class SwipeSchema(BaseModel):
    from_horse_id: str
    to_horse_id: str
    decision: SwipeDecisionValue

    def to_dto(self) -> SwipeDto:
        return SwipeDto(
            from_horse_id=self.from_horse_id,
            to_horse_id=self.to_horse_id,
            decision=self.decision.value,
            created_at=datetime.now(),
            is_match=False,
        )
