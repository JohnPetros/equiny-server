from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    owner_name: str
    account_id: str
    account_email: str


class AccountCreatedEvent(Event[Payload]):
    name: str = 'auth/account.created'

    def __init__(
        self,
        account_id: str,
        account_email: str,
        owner_name: str,
    ) -> None:
        payload = Payload(
            account_id=account_id,
            account_email=account_email,
            owner_name=owner_name,
        )
        super().__init__(AccountCreatedEvent.name, payload)
