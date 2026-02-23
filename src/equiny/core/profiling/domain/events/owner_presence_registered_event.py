from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    owner_id: str


class OwnerPresenceRegisteredEvent(Event[Payload]):
    NAME: str = 'profiling/owner.presence.registered'

    def __init__(self, owner_id: str) -> None:
        payload = Payload(
            owner_id=owner_id,
        )
        super().__init__(OwnerPresenceRegisteredEvent.NAME, payload)
