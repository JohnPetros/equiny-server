import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.domain.errors.invalid_credentials_error import (
    InvalidCredentialsError,
)
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.auth.interfaces.repositories import AccountsRepository
from equiny.core.auth.use_cases.sign_in_account_use_case import SignInAccountUseCase


class TestSignInAccountUseCase:
    hash_provider_mock: Mock
    jwt_provider_mock: Mock
    repository_mock: Mock
    use_case: SignInAccountUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.hash_provider_mock = create_autospec(HashProvider, instance=True)
        self.jwt_provider_mock = create_autospec(JwtProvider, instance=True)
        self.repository_mock = create_autospec(AccountsRepository, instance=True)

        self.hash_provider_mock.verify.return_value = True
        self.jwt_provider_mock.encode.return_value = 'jwt-token'

        account = Account.create(
            AccountDto(
                id='01ARZ3NDEKTSV4RRFFQ69G5FAV',
                email='user@example.com',
                password='hashed-password',
            )
        )
        self.repository_mock.find_by_email.return_value = account

        self.use_case = SignInAccountUseCase(
            repository=self.repository_mock,
            hash_provider=self.hash_provider_mock,
            jwt_provider=self.jwt_provider_mock,
        )

    def test_should_return_jwt_when_credentials_are_valid(self) -> None:
        result = self.use_case.execute(
            email='user@example.com', password='plain-password'
        )

        self.repository_mock.find_by_email.assert_called_once_with('user@example.com')
        self.hash_provider_mock.verify.assert_called_once_with(
            'plain-password', 'hashed-password'
        )
        self.jwt_provider_mock.encode.assert_called_once_with(
            '01ARZ3NDEKTSV4RRFFQ69G5FAV'
        )

        assert result == 'jwt-token'

    def test_should_raise_invalid_credentials_error_when_password_is_wrong(
        self,
    ) -> None:
        self.hash_provider_mock.verify.return_value = False

        with pytest.raises(InvalidCredentialsError):
            self.use_case.execute(email='user@example.com', password='wrong-password')

        self.repository_mock.find_by_email.assert_called_once_with('user@example.com')
        self.hash_provider_mock.verify.assert_called_once()
        self.jwt_provider_mock.encode.assert_not_called()

    def test_should_raise_invalid_credentials_error_when_account_not_found(
        self,
    ) -> None:
        self.repository_mock.find_by_email.return_value = None

        with pytest.raises(InvalidCredentialsError):
            self.use_case.execute(
                email='unknown@example.com', password='plain-password'
            )

        self.repository_mock.find_by_email.assert_called_once_with(
            'unknown@example.com'
        )
        self.hash_provider_mock.verify.assert_not_called()
        self.jwt_provider_mock.encode.assert_not_called()
