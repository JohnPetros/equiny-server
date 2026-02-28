from dataclasses import dataclass
from datetime import datetime

from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    horse_a_id: str
    horse_b_id: str
    created_at: str


class MatchCreatedEvent(Event[Payload]):
    NAME: str = 'matching/match.created'

    def __init__(self, horse_a_id: str, horse_b_id: str, created_at: datetime) -> None:
        payload = Payload(
            horse_a_id=horse_a_id,
            horse_b_id=horse_b_id,
            created_at=created_at.isoformat(),
        )
        super().__init__(MatchCreatedEvent.NAME, payload)
