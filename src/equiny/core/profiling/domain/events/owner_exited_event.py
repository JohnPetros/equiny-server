from dataclasses import dataclass

from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    owner_id: str


class OwnerExitedEvent(Event[Payload]):
    NAME: str = 'profiling/owner.exited'

    def __init__(self, owner_id: str) -> None:
        payload = Payload(
            owner_id=owner_id,
        )
        super().__init__(OwnerExitedEvent.NAME, payload)
