from equiny.core.auth.domain.structures.social_account import SocialAccount
from equiny.database.sqlalchemy.models.auth.social_account_model import (
    SocialAccountModel,
)


class SocialAccountsMapper:
    @staticmethod
    def to_entity(model: SocialAccountModel) -> SocialAccount:
        return SocialAccount.create(model.email, model.provider)

    @staticmethod
    def to_model(social_account: SocialAccount, account_id: str) -> SocialAccountModel:
        return SocialAccountModel(
            id=f'{account_id}:{social_account.provider.dto}',
            account_id=account_id,
            email=social_account.email.value,
            provider=social_account.provider.dto,
        )
