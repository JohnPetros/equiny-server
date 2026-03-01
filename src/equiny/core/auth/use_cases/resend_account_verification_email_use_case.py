from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.interfaces.providers.email_verification_provider import (
    EmailVerificationProvider,
)
from equiny.core.shared.interfaces.broker import Broker
from equiny.core.auth.domain.errors.account_not_found_error import AccountNotFoundError
from equiny.core.auth.domain.errors.account_already_verified_error import (
    AccountAlreadyVerifiedError,
)
from equiny.core.auth.domain.events.email_verification_requested_event import (
    EmailVerificationRequestedEvent,
)
from equiny.core.shared.domain.structures.email import Email


class ResendAccountVerificationEmailUseCase:
    def __init__(
        self,
        repository: AccountsRepository,
        email_verification_provider: EmailVerificationProvider,
        broker: Broker,
    ) -> None:
        self._repository = repository
        self._email_verification_provider = email_verification_provider
        self._broker = broker

    def execute(self, account_email: str) -> None:
        account = self._repository.find_by_email(Email.create(account_email))
        if account is None:
            raise AccountNotFoundError
        if account.is_verified.is_true:
            raise AccountAlreadyVerifiedError
        email = Email.create(account_email)
        token = self._email_verification_provider.generate_verification_token(email)
        self._broker.publish(
            EmailVerificationRequestedEvent(
                account_email=account_email, email_verification_token=token.value
            )
        )
