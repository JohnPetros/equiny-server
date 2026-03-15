import pytest
from unittest.mock import Mock, create_autospec

from src.equiny.core.notification.interfaces.email_sender_provider import EmailProvider
from src.equiny.core.notification.use_cases.send_account_verification_email_use_case import (
    SendAccountVerificationEmailUseCase,
)
from src.equiny.core.shared.domain.structures.email import Email
from src.equiny.core.shared.domain.structures.text import Text


class TestSendAccountVerificationEmailUseCase:
    email_sender_provider_mock: Mock
    use_case: SendAccountVerificationEmailUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.email_sender_provider_mock = create_autospec(EmailProvider, instance=True)

        self.use_case = SendAccountVerificationEmailUseCase(
            email_sender_provider=self.email_sender_provider_mock,
        )

    def test_should_send_verification_email_when_called(self) -> None:
        self.use_case.execute(
            account_email='user@example.com',
            email_verification_token='verification-token-123',  # noqa: S106
        )

        self.email_sender_provider_mock.send_account_verification_email.assert_called_once_with(
            Email.create('user@example.com'),
            Text.create('verification-token-123'),
        )
