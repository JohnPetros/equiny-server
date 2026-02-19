from datetime import datetime

from equiny.core.shared.domain.decorators import dto


@dto
class SwipeDto:
    from_horse_id: str
    to_horse_id: str
    created_at: datetime
    is_match: bool
    decision: str
