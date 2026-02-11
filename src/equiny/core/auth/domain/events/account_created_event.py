from equiny.core.shared.domain.abstracts import Event


class AccountCreatedEvent(Event):
    name: str = 'auth/account.created'
    account_id: str

    def __init__(self, account_id: str) -> None:
        super().__init__(name=AccountCreatedEvent.name)
        self.account_id = account_id
