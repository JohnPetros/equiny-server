from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.domain.structures.dtos.social_account_dto import SocialAccountDto
from equiny.database.sqlalchemy.mappers.auth.social_accounts_mapper import (
    SocialAccountsMapper,
)
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
            social_accounts=[
                SocialAccountDto(
                    email=social_account_model.email,
                    provider=social_account_model.provider,
                )
                for social_account_model in (account_model.social_accounts or [])
            ],
        )

    @staticmethod
    def to_model(account: Account) -> AccountModel:
        account_id = account.id.value
        return AccountModel(
            id=account_id,
            email=account.email.value,
            password=account.password.value if account.password is not None else None,
            is_verified=account.is_verified.value,
            social_accounts=[
                SocialAccountsMapper.to_model(social_account, account_id)
                for social_account in account.social_accounts
            ],
        )
