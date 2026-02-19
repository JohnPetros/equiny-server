from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.errors.invalid_credentials_error import (
    InvalidCredentialsError,
)
from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider


class SignInAccountUseCase:
    def __init__(
        self,
        repository: AccountsRepository,
        hash_provider: HashProvider,
        jwt_provider: JwtProvider,
    ) -> None:
        self.repository = repository
        self.hash_provider = hash_provider
        self.jwt_provider = jwt_provider

    def execute(self, email: str, password: str) -> str:
        account = self.find_account_by_email(email)
        is_valid_password = self.hash_provider.verify(password, account.password.value)

        if not is_valid_password:
            raise InvalidCredentialsError

        return self.jwt_provider.encode(account.id.value)

    def find_account_by_email(self, email: str) -> Account:
        account = self.repository.find_by_email(email)
        print('account', account)
        if account is None:
            raise InvalidCredentialsError
        return account
