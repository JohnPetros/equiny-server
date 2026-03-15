from typing import TYPE_CHECKING, cast
from unittest.mock import create_autospec

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.equiny.core.auth.domain.entities.account import Account
from src.equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from src.equiny.core.auth.interfaces.providers import GoogleAuthProvider
from src.equiny.core.shared.domain.errors import AuthError
from src.equiny.database.sqlalchemy.models.auth.account_model import AccountModel
from src.equiny.database.sqlalchemy.repositories.auth.sqlalchemy_accounts_repository import (
    SqlalchemyAccountsRepository,
)
from src.equiny.providers.hash import PwdlibHashProvider
from src.equiny.pipes import ProvidersPipe

if TYPE_CHECKING:
    from fastapi import FastAPI


class TestSignUpWithGoogleController:
    def test_should_sign_up_with_google_and_return_jwt(
        self, client: TestClient
    ) -> None:
        fastapi_app = cast('FastAPI', client.app)
        google_auth_provider = create_autospec(GoogleAuthProvider, instance=True)
        google_auth_provider.authenticate.return_value = (
            'google-user@example.com',
            'Google User',
        )
        fastapi_app.dependency_overrides[ProvidersPipe.get_google_auth_provider] = (
            lambda: google_auth_provider
        )

        try:
            response = client.post(
                '/auth/sign-up/google',
                json={'id_token': 'google-id-token'},
            )
        finally:
            fastapi_app.dependency_overrides.pop(
                ProvidersPipe.get_google_auth_provider,
                None,
            )

        assert response.status_code == 201
        data = response.json()
        assert data['access_token']
        assert data['refresh_token']

    def test_should_return_401_when_google_token_is_invalid(
        self, client: TestClient
    ) -> None:
        fastapi_app = cast('FastAPI', client.app)
        google_auth_provider = create_autospec(GoogleAuthProvider, instance=True)
        google_auth_provider.authenticate.side_effect = AuthError(
            'Token Google inválido'
        )
        fastapi_app.dependency_overrides[ProvidersPipe.get_google_auth_provider] = (
            lambda: google_auth_provider
        )

        try:
            response = client.post(
                '/auth/sign-up/google',
                json={'id_token': 'invalid-google-id-token'},
            )
        finally:
            fastapi_app.dependency_overrides.pop(
                ProvidersPipe.get_google_auth_provider,
                None,
            )

        assert response.status_code == 401
        assert response.json()['message'] == 'Token Google inválido'

    def test_should_sign_up_twice_with_google_without_duplicating_social_account(
        self,
        client: TestClient,
        sqlalchemy_session: Session,
    ) -> None:
        fastapi_app = cast('FastAPI', client.app)
        google_auth_provider = create_autospec(GoogleAuthProvider, instance=True)
        google_auth_provider.authenticate.return_value = (
            'double-sign-up@example.com',
            'Double Sign Up',
        )
        fastapi_app.dependency_overrides[ProvidersPipe.get_google_auth_provider] = (
            lambda: google_auth_provider
        )

        try:
            first_response = client.post(
                '/auth/sign-up/google',
                json={'id_token': 'google-id-token'},
            )
            second_response = client.post(
                '/auth/sign-up/google',
                json={'id_token': 'google-id-token'},
            )
        finally:
            fastapi_app.dependency_overrides.pop(
                ProvidersPipe.get_google_auth_provider,
                None,
            )

        sqlalchemy_session.expire_all()
        persisted_account = (
            sqlalchemy_session.query(AccountModel)
            .filter(AccountModel.email == 'double-sign-up@example.com')
            .one()
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 201
        assert len(persisted_account.social_accounts) == 1
        assert persisted_account.social_accounts[0].provider == 'google'

    def test_should_return_422_when_id_token_is_missing(
        self, client: TestClient
    ) -> None:
        response = client.post('/auth/sign-up/google', json={})

        assert response.status_code == 422
        assert response.json()['title'] == 'Erro de validação'

    def test_should_return_informative_error_when_signing_in_with_password_for_google_account(
        self,
        client: TestClient,
    ) -> None:
        fastapi_app = cast('FastAPI', client.app)
        google_auth_provider = create_autospec(GoogleAuthProvider, instance=True)
        google_auth_provider.authenticate.return_value = (
            'google-passwordless@example.com',
            'Google User',
        )
        fastapi_app.dependency_overrides[ProvidersPipe.get_google_auth_provider] = (
            lambda: google_auth_provider
        )

        try:
            sign_up_response = client.post(
                '/auth/sign-up/google',
                json={'id_token': 'google-id-token'},
            )
            response = client.post(
                '/auth/sign-in',
                json={
                    'email': 'google-passwordless@example.com',
                    'password': 'plain-password',
                },
            )
        finally:
            fastapi_app.dependency_overrides.pop(
                ProvidersPipe.get_google_auth_provider,
                None,
            )

        assert sign_up_response.status_code == 201
        assert response.status_code == 401
        assert (
            response.json()['message'] == 'Esta conta usa Google. Entre com o Google.'
        )

    def test_should_link_google_to_existing_account_without_creating_duplicate_account(
        self,
        client: TestClient,
        sqlalchemy_session: Session,
    ) -> None:
        fastapi_app = cast('FastAPI', client.app)
        google_auth_provider = create_autospec(GoogleAuthProvider, instance=True)
        google_auth_provider.authenticate.return_value = (
            'existing@example.com',
            'Existing User',
        )
        fastapi_app.dependency_overrides[ProvidersPipe.get_google_auth_provider] = (
            lambda: google_auth_provider
        )

        password_hash = PwdlibHashProvider().generate('plain-password')
        account = Account.create(
            AccountDto(
                email='existing@example.com',
                password=password_hash,
                is_verified=False,
            )
        )
        SqlalchemyAccountsRepository(sqlalchemy_session).add(account)
        sqlalchemy_session.commit()

        try:
            response = client.post(
                '/auth/sign-up/google',
                json={'id_token': 'google-id-token'},
            )
        finally:
            fastapi_app.dependency_overrides.pop(
                ProvidersPipe.get_google_auth_provider,
                None,
            )

        sqlalchemy_session.expire_all()
        persisted_account = (
            sqlalchemy_session.query(AccountModel)
            .filter(AccountModel.email == 'existing@example.com')
            .one()
        )

        assert response.status_code == 201
        assert persisted_account.email == 'existing@example.com'
        assert persisted_account.is_verified is True
        assert persisted_account.password is not None
        assert len(persisted_account.social_accounts) == 1
        assert persisted_account.social_accounts[0].provider == 'google'
