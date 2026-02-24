from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    owner_id: str


class OwnerEnteredEvent(Event[Payload]):
    name: str = 'profiling/owner.entered'

    def __init__(self, owner_id: str) -> None:
        payload = Payload(
            owner_id=owner_id,
        )
        super().__init__(OwnerEnteredEvent.name, payload)
