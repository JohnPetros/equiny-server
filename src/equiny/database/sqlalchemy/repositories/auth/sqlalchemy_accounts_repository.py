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


class SqlalchemyAccountsRepository(SqlalchemyRepository, AccountsRepository):
    def add(self, account: Account) -> None:
        account_model = AccountsMapper.to_model(account)
        self.sqlalchemy.add(account_model)

    def find_by_id(self, id: str) -> Account | None:
        account_model = (
            self.sqlalchemy.query(AccountModel).filter(AccountModel.id == id).first()
        )
        if account_model is None:
            return None
        return AccountsMapper.to_entity(account_model)
