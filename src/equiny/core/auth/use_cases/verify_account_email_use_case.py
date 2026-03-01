from equiny.core.auth.interfaces.providers.email_verification_provider import (
    EmailVerificationProvider,
)
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.domain.errors.invalid_email_verification_token_error import (
    InvalidEmailVerificationTokenError,
)
from equiny.core.auth.domain.errors.account_not_found_error import AccountNotFoundError
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text
from equiny.core.shared.domain.structures.logical import Logical


class VerifyAccountEmailUseCase:
    def __init__(
        self,
        email_verification_provider: EmailVerificationProvider,
        repository: AccountsRepository,
    ) -> None:
        self._email_verification_provider = email_verification_provider
        self._repository = repository

    def execute(self, verification_token: str) -> None:
        token = Text.create(verification_token)
        result = self._email_verification_provider.verify_verification_token(token)
        if result.is_false:
            raise InvalidEmailVerificationTokenError
        account_email = self._email_verification_provider.decode_email_from_token(token)
        account = self._repository.find_by_email(Email.create(account_email))
        if account is None:
            raise AccountNotFoundError
        if account.is_verified.is_true:
            return
        account.is_verified = Logical.create_true()
        self._repository.update(account)
