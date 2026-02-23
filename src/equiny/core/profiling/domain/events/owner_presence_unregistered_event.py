from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    owner_id: str


class OwnerPresenceUnregisteredEvent(Event[Payload]):
    NAME: str = 'profiling/owner.presence.unregistered'

    def __init__(self, owner_id: str) -> None:
        payload = Payload(
            owner_id=owner_id,
        )
        super().__init__(OwnerPresenceUnregisteredEvent.NAME, payload)
