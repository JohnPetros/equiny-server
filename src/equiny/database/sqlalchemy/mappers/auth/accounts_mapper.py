from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.database.sqlalchemy.models.auth.account_model import AccountModel


class AccountsMapper:
    @staticmethod
    def to_entity(account_model: AccountModel) -> Account:
        return Account.create(AccountsMapper.to_dto(account_model))

    @staticmethod
    def to_dto(account_model: AccountModel) -> AccountDto:
        return AccountDto(
            id=account_model.id,
            email=account_model.email,
            password=account_model.password,
            is_verified=account_model.is_verified,
        )

    @staticmethod
    def to_model(account: Account) -> AccountModel:
        return AccountModel(
            id=account.id.value,
            email=account.email.value,
            password=account.password.value,
            is_verified=account.is_verified.value,
        )
