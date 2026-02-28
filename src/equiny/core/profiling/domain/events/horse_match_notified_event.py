from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event
from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto


@dataclass
class _Payload:
    horse_match: HorseMatchDto


class HorseMatchNotifiedEvent(Event[_Payload]):
    NAME: str = 'profiling/horse.match.notified'

    def __init__(self, horse_match: HorseMatchDto) -> None:
        payload = _Payload(
            horse_match=horse_match,
        )
        super().__init__(HorseMatchNotifiedEvent.NAME, payload)
        self.horse_match = horse_match
