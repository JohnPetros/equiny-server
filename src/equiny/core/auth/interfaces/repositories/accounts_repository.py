from typing import Protocol
from equiny.core.auth.domain.entities.account import Account


class AccountsRepository(Protocol):
    def add(self, account: Account) -> None: ...

    def find_by_email(self, email: str) -> Account | None: ...

    def find_by_id(self, id: str) -> Account | None: ...
