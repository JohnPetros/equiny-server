from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    account_id: str
    owner_name: str


class AccountCreatedEvent(Event):
    name: str = 'auth/account.created'

    def __init__(self, account_id: str, owner_name: str) -> None:
        payload = Payload(account_id=account_id, owner_name=owner_name)
        super().__init__(AccountCreatedEvent.name, payload)
