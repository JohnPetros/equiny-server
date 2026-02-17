from equiny.core.shared.domain.decorators import dto
from datetime import datetime


@dto
class MatchDto:
    horse_a_id: str
    horse_b_id: str
    created_at: datetime
