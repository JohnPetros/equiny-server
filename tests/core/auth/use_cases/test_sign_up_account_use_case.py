from unittest.mock import Mock, call, create_autospec

import pytest

from equiny.core.auth.domain.errors.email_already_in_use_error import (
    EmailAlreadyInUseError,
)
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.auth.interfaces.repositories import AccountsRepository
from equiny.core.auth.use_cases.sign_up_account_use_case import SignUpAccountUseCase
from equiny.core.shared.domain.errors import ValidationError
from equiny.core.shared.interfaces import Broker


class TestSignUpAccountUseCase:
    hash_provider_mock: Mock
    jwt_provider_mock: Mock
    repository_mock: Mock
    broker_mock: Mock
    use_case: SignUpAccountUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.hash_provider_mock = create_autospec(HashProvider, instance=True)
        self.jwt_provider_mock = create_autospec(JwtProvider, instance=True)
        self.repository_mock = create_autospec(AccountsRepository, instance=True)
        self.broker_mock = create_autospec(Broker, instance=True)

        self.hash_provider_mock.generate.return_value = 'hashed-password'
        self.repository_mock.find_by_email.return_value = None

        self.use_case = SignUpAccountUseCase(
            hash_provider=self.hash_provider_mock,
            repository=self.repository_mock,
            broker=self.broker_mock,
        )

    def test_should_create_account_and_publish_event_when_input_is_valid(self) -> None:
        result = self.use_case.execute(
            account_email='owner@example.com',
            account_password='plain-password',  # noqa: S106
            owner_name='John Owner',
        )

        self.hash_provider_mock.generate.assert_called_once_with('plain-password')
        self.repository_mock.find_by_email.assert_called_once_with('owner@example.com')
        self.repository_mock.add.assert_called_once()
        self.broker_mock.publish.assert_called_once()

        captured_account = self.repository_mock.add.call_args[0][0]
        published_event = self.broker_mock.publish.call_args[0][0]

        assert result.id == captured_account.id.value
        assert result.email == 'owner@example.com'
        assert not hasattr(result, 'password')
        assert published_event.name == 'auth/account.created'
        assert published_event.payload.account_id == result.id
        assert published_event.payload.owner_name == 'John Owner'

        self.repository_mock.assert_has_calls(
            [
                call.find_by_email('owner@example.com'),
                call.add(captured_account),
            ]
        )

    def test_should_raise_validation_error_when_email_is_invalid(self) -> None:
        with pytest.raises(ValidationError):
            self.use_case.execute(
                account_email='invalid-email',
                account_password='plain-password',  # noqa: S106
                owner_name='John Owner',
            )

        self.hash_provider_mock.generate.assert_called_once_with('plain-password')
        self.repository_mock.find_by_email.assert_called_once_with('invalid-email')
        self.repository_mock.add.assert_not_called()
        self.broker_mock.publish.assert_not_called()

    def test_should_raise_email_already_in_use_error_when_email_exists(self) -> None:
        self.repository_mock.find_by_email.return_value = Mock()

        with pytest.raises(EmailAlreadyInUseError) as exc_info:
            self.use_case.execute(
                account_email='existing@example.com',
                account_password='plain-password',  # noqa: S106
                owner_name='John Owner',
            )

        assert exc_info.value.message == 'Email existing@example.com já está em uso'
        self.repository_mock.find_by_email.assert_called_once_with(
            'existing@example.com'
        )
        self.repository_mock.add.assert_not_called()
        self.broker_mock.publish.assert_not_called()
