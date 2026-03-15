import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.domain.errors.invalid_email_verification_token_error import (
    InvalidEmailVerificationTokenError,
)
from equiny.core.auth.domain.errors.account_not_found_error import (
    AccountNotFoundError,
)
from equiny.core.auth.interfaces.providers.email_verification_provider import (
    EmailVerificationProvider,
)
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.use_cases.verify_account_email_use_case import (
    VerifyAccountEmailUseCase,
)
from equiny.core.shared.domain.structures.logical import Logical
from equiny.core.shared.domain.structures.text import Text


class TestVerifyAccountEmailUseCase:
    email_verification_provider_mock: Mock
    repository_mock: Mock
    use_case: VerifyAccountEmailUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.email_verification_provider_mock = create_autospec(
            EmailVerificationProvider, instance=True
        )
        self.repository_mock = create_autospec(AccountsRepository, instance=True)

        self.use_case = VerifyAccountEmailUseCase(
            email_verification_provider=self.email_verification_provider_mock,
            repository=self.repository_mock,
        )

    def test_should_verify_account_when_token_is_valid(self) -> None:
        account = Account.create(
            AccountDto(
                id='01ARZ3NDEKTSV4RRFFQ69G5FAV',
                email='user@example.com',
                password='hashed-password',  # noqa: S106
                is_verified=False,
            )
        )
        self.email_verification_provider_mock.verify_verification_token.return_value = (
            Logical.create_true()
        )
        self.email_verification_provider_mock.decode_email_from_token.return_value = (
            'user@example.com'
        )
        self.repository_mock.find_by_email.return_value = account

        self.use_case.execute(verification_token='valid-token')  # noqa: S106

        self.email_verification_provider_mock.verify_verification_token.assert_called_once_with(
            Text.create('valid-token')
        )
        self.email_verification_provider_mock.decode_email_from_token.assert_called_once_with(
            Text.create('valid-token')
        )
        self.repository_mock.find_by_email.assert_called_once()
        self.repository_mock.update.assert_called_once_with(account)
        assert account.is_verified.is_true

    def test_should_return_when_account_is_already_verified(self) -> None:
        account = Account.create(
            AccountDto(
                id='01ARZ3NDEKTSV4RRFFQ69G5FAV',
                email='user@example.com',
                password='hashed-password',  # noqa: S106
                is_verified=True,
            )
        )
        self.email_verification_provider_mock.verify_verification_token.return_value = (
            Logical.create_true()
        )
        self.email_verification_provider_mock.decode_email_from_token.return_value = (
            'user@example.com'
        )
        self.repository_mock.find_by_email.return_value = account

        self.use_case.execute(verification_token='valid-token')  # noqa: S106

        self.email_verification_provider_mock.verify_verification_token.assert_called_once()
        self.repository_mock.find_by_email.assert_called_once()
        self.repository_mock.update.assert_not_called()

    def test_should_raise_invalid_token_error_when_token_is_invalid(
        self,
    ) -> None:
        self.email_verification_provider_mock.verify_verification_token.return_value = (
            Logical.create_false()
        )

        with pytest.raises(InvalidEmailVerificationTokenError):
            self.use_case.execute(verification_token='invalid-token')  # noqa: S106

        self.email_verification_provider_mock.verify_verification_token.assert_called_once_with(
            Text.create('invalid-token')
        )
        self.email_verification_provider_mock.decode_email_from_token.assert_not_called()
        self.repository_mock.find_by_email.assert_not_called()
        self.repository_mock.update.assert_not_called()

    def test_should_raise_account_not_found_error_when_account_does_not_exist(
        self,
    ) -> None:
        self.email_verification_provider_mock.verify_verification_token.return_value = (
            Logical.create_true()
        )
        self.email_verification_provider_mock.decode_email_from_token.return_value = (
            'nonexistent@example.com'
        )
        self.repository_mock.find_by_email.return_value = None

        with pytest.raises(AccountNotFoundError):
            self.use_case.execute(verification_token='valid-token')  # noqa: S106

        self.email_verification_provider_mock.verify_verification_token.assert_called_once()
        self.email_verification_provider_mock.decode_email_from_token.assert_called_once()
        self.repository_mock.find_by_email.assert_called_once()
        self.repository_mock.update.assert_not_called()
