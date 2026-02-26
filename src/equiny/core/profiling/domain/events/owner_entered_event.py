from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class _Payload:
    owner_id: str


class OwnerEnteredEvent(Event[_Payload]):
    NAME: str = 'profiling/owner.entered'

    def __init__(self, owner_id: str) -> None:
        payload = _Payload(
            owner_id=owner_id,
        )
        super().__init__(OwnerEnteredEvent.name, payload)
