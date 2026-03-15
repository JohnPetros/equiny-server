from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.domain.entities.dtos.sign_up_result_dto import SignUpResultDto
from equiny.core.auth.domain.errors.email_already_in_use_error import (
    EmailAlreadyInUseError,
)
from equiny.core.auth.interfaces.providers.email_verification_provider import (
    EmailVerificationProvider,
)
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.auth.interfaces.repositories import AccountsRepository
from equiny.core.shared.interfaces import Broker
from equiny.core.auth.domain.events import AccountCreatedEvent
from equiny.core.shared.domain.structures.email import Email


class SignUpAccountUseCase:
    def __init__(
        self,
        hash_provider: HashProvider,
        repository: AccountsRepository,
        email_verification_provider: EmailVerificationProvider,
        broker: Broker,
    ) -> None:
        self._hash_provider = hash_provider
        self._repository = repository
        self._email_verification_provider = email_verification_provider
        self._broker = broker

    def execute(
        self,
        account_email: str,
        account_password: str,
        owner_name: str,
    ) -> SignUpResultDto:
        self.find_account_by_email(account_email)
        hashed_password = self._hash_provider.generate(account_password)
        account = Account.create(
            AccountDto(
                email=account_email,
                password=hashed_password,
                is_verified=False,
                social_accounts=[],
            )
        )
        self._repository.add(account)
        email_verification_token = (
            self._email_verification_provider.generate_verification_token(account.email)
        )
        self._broker.publish(
            AccountCreatedEvent(
                account_id=account.id.value,
                account_email=account_email,
                owner_name=owner_name,
                account_email_verification_token=email_verification_token.value,
            )
        )
        return SignUpResultDto(
            id=account.id.value,
            email=account.email.value,
            is_verified=account.is_verified.value,
        )

    def find_account_by_email(self, email: str) -> None:
        account = self._repository.find_by_email(Email.create(email))
        if account:
            raise EmailAlreadyInUseError(email)
