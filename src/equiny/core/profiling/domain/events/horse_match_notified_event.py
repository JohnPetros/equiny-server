from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event
from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto


@dataclass
class _Payload:
    horse_match: HorseMatchDto
    owner_id: str


class HorseMatchNotifiedEvent(Event[_Payload]):
    NAME: str = 'profiling/horse.match.notified'

    def __init__(self, horse_match: HorseMatchDto, owner_id: str) -> None:
        payload = _Payload(
            horse_match=horse_match,
            owner_id=owner_id,
        )
        super().__init__(HorseMatchNotifiedEvent.NAME, payload)
        self.horse_match = horse_match
        self.owner_id = owner_id
