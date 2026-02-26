from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class _Payload:
    owner_id: str
    owner_matches: list[str]


class OwnerPresenceRegisteredEvent(Event[_Payload]):
    NAME: str = 'profiling/owner.presence.registered'

    def __init__(self, owner_id: str, owner_matches: list[str]) -> None:
        payload = _Payload(
            owner_id=owner_id,
            owner_matches=owner_matches,
        )
        super().__init__(OwnerPresenceRegisteredEvent.NAME, payload)
