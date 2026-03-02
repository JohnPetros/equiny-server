from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.database.sqlalchemy.mappers.auth.accounts_mapper import (
    AccountsMapper,
)
from equiny.database.sqlalchemy.models.auth.account_model import AccountModel
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.email import Email


class SqlalchemyAccountsRepository(SqlalchemyRepository, AccountsRepository):
    def add(self, account: Account) -> None:
        account_model = AccountsMapper.to_model(account)
        self.sqlalchemy.add(account_model)

    def add_many(self, accounts: list[Account]) -> None:
        account_models = [AccountsMapper.to_model(account) for account in accounts]
        self.sqlalchemy.add_all(account_models)

    def find_by_email(self, email: Email) -> Account | None:
        account_model = (
            self.sqlalchemy.query(AccountModel)
            .filter(AccountModel.email == email.value)
            .first()
        )
        if account_model is None:
            return None
        return AccountsMapper.to_entity(account_model)

    def find_by_id(self, id: Id) -> Account | None:
        account_model = (
            self.sqlalchemy.query(AccountModel)
            .filter(AccountModel.id == id.value)
            .first()
        )
        if account_model is None:
            return None
        return AccountsMapper.to_entity(account_model)

    def update(self, account: Account) -> None:
        account_model = (
            self.sqlalchemy.query(AccountModel)
            .filter(AccountModel.id == account.id.value)
            .first()
        )
        if account_model is None:
            return
        account_model.is_verified = account.is_verified.value
