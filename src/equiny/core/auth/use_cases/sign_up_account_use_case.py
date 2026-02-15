from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.domain.entities.dtos.sign_up_result_dto import SignUpResultDto
from equiny.core.auth.domain.errors.email_already_in_use_error import (
    EmailAlreadyInUseError,
)
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.auth.interfaces.repositories import AccountsRepository
from equiny.core.shared.interfaces import Broker
from equiny.core.auth.domain.events import AccountCreatedEvent


class SignUpAccountUseCase:
    def __init__(
        self,
        hash_provider: HashProvider,
        repository: AccountsRepository,
        broker: Broker,
    ) -> None:
        self.hash_provider = hash_provider
        self.repository = repository
        self.broker = broker

    def execute(
        self,
        account_email: str,
        account_password: str,
        owner_name: str,
    ) -> SignUpResultDto:
        self.find_account_by_email(account_email)
        hashed_password = self.hash_provider.generate(account_password)
        account = Account.create(
            AccountDto(email=account_email, password=hashed_password)
        )
        self.repository.add(account)
        self.broker.publish(
            AccountCreatedEvent(
                account_id=account.id.value,
                account_email=account_email,
                owner_name=owner_name,
            )
        )
        return SignUpResultDto(id=account.id.value, email=account.email.value)

    def find_account_by_email(self, email: str) -> None:
        account = self.repository.find_by_email(email)
        if account:
            raise EmailAlreadyInUseError(email)
