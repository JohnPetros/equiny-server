from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class _Payload:
    owner_id: str
    owner_email: str
    owner_email_verification_token: str


class OwnerCreatedEvent(Event[_Payload]):
    NAME: str = 'profiling/owner.created'

    def __init__(
        self, owner_id: str, owner_email: str, owner_email_verification_token: str
    ) -> None:
        payload = _Payload(
            owner_id=owner_id,
            owner_email=owner_email,
            owner_email_verification_token=owner_email_verification_token,
        )
        super().__init__(OwnerCreatedEvent.NAME, payload)
