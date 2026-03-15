from secrets import token_urlsafe
from unittest.mock import Mock, create_autospec

import pytest

from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.domain.structures.dtos.jwt_dto import JwtDto
from equiny.core.auth.domain.structures.dtos.social_account_dto import (
    SocialAccountDto,
)
from equiny.core.auth.interfaces.providers import GoogleAuthProvider, JwtProvider
from equiny.core.auth.interfaces.repositories import AccountsRepository
from equiny.core.auth.use_cases import SignUpWithGoogleUseCase
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.interfaces.broker import Broker


class TestSignUpWithGoogleUseCase:
    repository_mock: Mock
    google_auth_provider_mock: Mock
    jwt_provider_mock: Mock
    broker_mock: Mock
    use_case: SignUpWithGoogleUseCase
    jwt_dto: JwtDto

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(AccountsRepository, instance=True)
        self.google_auth_provider_mock = create_autospec(
            GoogleAuthProvider, instance=True
        )
        self.jwt_provider_mock = create_autospec(JwtProvider, instance=True)
        self.broker_mock = create_autospec(Broker, instance=True)

        self.google_auth_provider_mock.authenticate.return_value = (
            'owner@example.com',
            'John Owner',
        )
        self.jwt_dto = JwtDto(
            access_token=token_urlsafe(32),
            refresh_token=token_urlsafe(32),
        )
        self.jwt_provider_mock.encode.return_value = self.jwt_dto
        self.repository_mock.find_by_email.return_value = None

        self.use_case = SignUpWithGoogleUseCase(
            repository=self.repository_mock,
            google_auth_provider=self.google_auth_provider_mock,
            jwt_provider=self.jwt_provider_mock,
            broker=self.broker_mock,
        )

    def test_should_create_account_and_publish_event_when_account_does_not_exist(
        self,
    ) -> None:
        result = self.use_case.execute('google-token')

        self.repository_mock.find_by_email.assert_called_once_with(
            Email.create('owner@example.com')
        )
        self.repository_mock.add.assert_called_once()
        self.repository_mock.update.assert_not_called()
        self.broker_mock.publish.assert_called_once()
        self.jwt_provider_mock.encode.assert_called_once()

        created_account = self.repository_mock.add.call_args[0][0]
        published_event = self.broker_mock.publish.call_args[0][0]

        assert created_account.password is None
        assert created_account.is_verified.value is True
        assert len(created_account.social_accounts) == 1
        assert created_account.social_accounts[0].provider.dto == 'google'
        assert published_event.payload.account_email_verification_token is None
        assert result.access_token == self.jwt_dto.access_token
        assert result.refresh_token == self.jwt_dto.refresh_token

    def test_should_link_google_and_return_jwt_when_account_already_exists(
        self,
    ) -> None:
        existing_account = Account.create(
            AccountDto(
                id='01ARZ3NDEKTSV4RRFFQ69G5FAV',
                email='owner@example.com',
                password='hashed-password',  # noqa: S106
                is_verified=False,
            )
        )

        self.repository_mock.reset_mock()
        self.jwt_provider_mock.reset_mock()
        self.broker_mock.reset_mock()
        self.repository_mock.find_by_email.return_value = existing_account

        result = self.use_case.execute('google-token')

        self.repository_mock.add.assert_not_called()
        self.repository_mock.update.assert_called_once_with(existing_account)
        self.broker_mock.publish.assert_not_called()
        assert len(existing_account.social_accounts) == 1
        assert existing_account.social_accounts[0].provider.dto == 'google'
        assert existing_account.is_verified.value is True
        assert result.access_token == self.jwt_dto.access_token
        assert result.refresh_token == self.jwt_dto.refresh_token

    def test_should_not_duplicate_google_link_when_account_already_has_provider(
        self,
    ) -> None:
        existing_account = Account.create(
            AccountDto(
                id='01ARZ3NDEKTSV4RRFFQ69G5FAV',
                email='owner@example.com',
                password=None,
                is_verified=True,
                social_accounts=[
                    SocialAccountDto(
                        email='owner@example.com',
                        provider='google',
                    )
                ],
            )
        )
        self.repository_mock.find_by_email.return_value = existing_account

        result = self.use_case.execute('google-token')

        self.repository_mock.add.assert_not_called()
        self.repository_mock.update.assert_called_once_with(existing_account)
        self.broker_mock.publish.assert_not_called()
        assert len(existing_account.social_accounts) == 1
        assert result.access_token == self.jwt_dto.access_token
        assert result.refresh_token == self.jwt_dto.refresh_token
