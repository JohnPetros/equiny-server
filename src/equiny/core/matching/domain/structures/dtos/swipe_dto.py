from datetime import datetime

from equiny.core.shared.domain.decorators import dto
from equiny.core.matching.domain.structures.swipe_decision import SwipeDecisionValue


@dto
class SwipeDto:
    from_horse_id: str
    to_horse_id: str
    created_at: datetime
    decision: SwipeDecisionValue
