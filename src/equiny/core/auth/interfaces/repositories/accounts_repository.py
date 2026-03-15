from typing import Protocol
from equiny.core.auth.domain.entities.account import Account
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.email import Email


class AccountsRepository(Protocol):
    def add(self, account: Account) -> None: ...

    def add_many(self, accounts: list[Account]) -> None: ...

    def find_by_email(self, email: Email) -> Account | None: ...

    def find_by_id(self, id: Id) -> Account | None: ...

    def update(self, account: Account) -> None:
        """Sync password, verification state and social accounts."""
