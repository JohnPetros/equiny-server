from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    participant_id: str


class OwnerEnteredEvent(Event[Payload]):
    name: str = 'profiling/owner.entered'

    def __init__(self, participant_id: str) -> None:
        payload = Payload(
            participant_id=participant_id,
        )
        super().__init__(OwnerEnteredEvent.name, payload)
