from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.domain.events import AccountCreatedEvent
from equiny.core.auth.domain.structures.social_account import SocialAccount
from equiny.core.auth.domain.structures.dtos.jwt_dto import JwtDto
from equiny.core.auth.interfaces.providers import GoogleAuthProvider, JwtProvider
from equiny.core.auth.interfaces.repositories import AccountsRepository
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text
from equiny.core.shared.interfaces import Broker


class SignUpWithGoogleUseCase:
    def __init__(
        self,
        repository: AccountsRepository,
        google_auth_provider: GoogleAuthProvider,
        jwt_provider: JwtProvider,
        broker: Broker,
    ) -> None:
        self._repository = repository
        self._google_auth_provider = google_auth_provider
        self._jwt_provider = jwt_provider
        self._broker = broker

    def execute(self, id_token: str) -> JwtDto:
        email, name = self._google_auth_provider.authenticate(Text.create(id_token))
        account = self._repository.find_by_email(Email.create(email))

        if account is None:
            account = Account.create(
                AccountDto(
                    email=email,
                    password=None,
                    is_verified=True,
                    social_accounts=[
                        SocialAccount.create(email, 'google').dto,
                    ],
                )
            )
            self._repository.add(account)
            self._broker.publish(
                AccountCreatedEvent(
                    account_id=account.id.value,
                    account_email=account.email.value,
                    owner_name=name,
                    account_email_verification_token=None,
                )
            )
            return self._jwt_provider.encode(account.id.value)

        account.is_verified = account.is_verified.create_true()
        if not any(
            social_account.provider.dto == 'google'
            for social_account in account.social_accounts
        ):
            account.social_accounts.append(SocialAccount.create(email, 'google'))
        self._repository.update(account)
        return self._jwt_provider.encode(account.id.value)
