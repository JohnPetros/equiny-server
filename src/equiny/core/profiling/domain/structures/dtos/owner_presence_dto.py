from datetime import datetime
from equiny.core.shared.domain.decorators.dto import dto


@dto
class OwnerPresenceDto:
    owner_id: str
    is_online: bool
    last_seen_at: datetime | None = None
