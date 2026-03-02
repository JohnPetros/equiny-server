from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    account_email: str
    email_verification_token: str


class EmailVerificationRequestedEvent(Event[Payload]):
    name: str = 'auth/email.verification.requested'

    def __init__(
        self,
        account_email: str,
        email_verification_token: str,
    ) -> None:
        payload = Payload(
            account_email=account_email,
            email_verification_token=email_verification_token,
        )
        super().__init__(EmailVerificationRequestedEvent.name, payload)
