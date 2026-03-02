import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.domain.errors.account_not_found_error import AccountNotFoundError
from equiny.core.auth.domain.errors.account_already_verified_error import (
    AccountAlreadyVerifiedError,
)
from equiny.core.auth.interfaces.providers.email_verification_provider import (
    EmailVerificationProvider,
)
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.use_cases.resend_account_verification_email_use_case import (
    ResendAccountVerificationEmailUseCase,
)
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text
from equiny.core.shared.interfaces.broker import Broker


class TestResendAccountVerificationEmailUseCase:
    repository_mock: Mock
    email_verification_provider_mock: Mock
    broker_mock: Mock
    use_case: ResendAccountVerificationEmailUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(AccountsRepository, instance=True)
        self.email_verification_provider_mock = create_autospec(
            EmailVerificationProvider, instance=True
        )
        self.broker_mock = create_autospec(Broker, instance=True)

        self.use_case = ResendAccountVerificationEmailUseCase(
            repository=self.repository_mock,
            email_verification_provider=self.email_verification_provider_mock,
            broker=self.broker_mock,
        )

    def test_should_publish_event_when_account_exists_and_not_verified(
        self,
    ) -> None:
        account = Account.create(
            AccountDto(
                id='01ARZ3NDEKTSV4RRFFQ69G5FAV',
                email='user@example.com',
                password='hashed-password',  # noqa: S106
                is_verified=False,
            )
        )
        self.repository_mock.find_by_email.return_value = account
        self.email_verification_provider_mock.generate_verification_token.return_value = Text.create(
            'generated-token'
        )

        self.use_case.execute(account_email='user@example.com')

        self.repository_mock.find_by_email.assert_called_once_with(
            Email.create('user@example.com')
        )
        self.email_verification_provider_mock.generate_verification_token.assert_called_once_with(
            Email.create('user@example.com')
        )
        self.broker_mock.publish.assert_called_once()
        call_args = self.broker_mock.publish.call_args
        event = call_args[0][0]
        assert event.payload_data['account_email'] == 'user@example.com'
        assert event.payload_data['email_verification_token'] == 'generated-token'  # noqa: S105

    def test_should_raise_account_not_found_error_when_account_does_not_exist(
        self,
    ) -> None:
        self.repository_mock.find_by_email.return_value = None

        with pytest.raises(AccountNotFoundError):
            self.use_case.execute(account_email='nonexistent@example.com')

        self.repository_mock.find_by_email.assert_called_once_with(
            Email.create('nonexistent@example.com')
        )
        self.email_verification_provider_mock.generate_verification_token.assert_not_called()
        self.broker_mock.publish.assert_not_called()

    def test_should_raise_account_already_verified_error_when_account_is_already_verified(
        self,
    ) -> None:
        account = Account.create(
            AccountDto(
                id='01ARZ3NDEKTSV4RRFFQ69G5FAV',
                email='user@example.com',
                password='hashed-password',  # noqa: S106
                is_verified=True,
            )
        )
        self.repository_mock.find_by_email.return_value = account

        with pytest.raises(AccountAlreadyVerifiedError):
            self.use_case.execute(account_email='user@example.com')

        self.repository_mock.find_by_email.assert_called_once_with(
            Email.create('user@example.com')
        )
        self.email_verification_provider_mock.generate_verification_token.assert_not_called()
        self.broker_mock.publish.assert_not_called()
