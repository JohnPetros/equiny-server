from unittest.mock import Mock, patch

import pytest

from src.equiny.core.shared.domain.errors import AuthError
from src.equiny.core.shared.domain.structures.text import Text
from src.equiny.providers.auth.google.google_auth_provider import GoogleOauthProvider


class TestGoogleOauthProvider:
    @patch(
        'equiny.providers.auth.google.google_auth_provider.Env.GOOGLE_OAUTH_CLIENT_ID',
        'google-client-id',
    )
    @patch('equiny.providers.auth.google.google_auth_provider.Request')
    @patch('equiny.providers.auth.google.google_auth_provider.verify_oauth2_token')
    def test_should_return_email_and_name_when_token_is_valid(
        self,
        verify_oauth2_token_mock: Mock,
        request_mock: Mock,
    ) -> None:
        verify_oauth2_token_mock.return_value = {
            'email': 'google-user@example.com',
            'name': 'Google User',
            'email_verified': True,
        }

        result = GoogleOauthProvider().authenticate(Text.create('google-id-token'))

        request_mock.assert_called_once_with()
        verify_oauth2_token_mock.assert_called_once()
        assert result == ('google-user@example.com', 'Google User')

    @patch(
        'equiny.providers.auth.google.google_auth_provider.Env.GOOGLE_OAUTH_CLIENT_ID',
        'google-client-id',
    )
    @patch('equiny.providers.auth.google.google_auth_provider.Request')
    @patch('equiny.providers.auth.google.google_auth_provider.verify_oauth2_token')
    def test_should_raise_auth_error_when_email_is_not_verified(
        self,
        verify_oauth2_token_mock: Mock,
        _: Mock,
    ) -> None:
        verify_oauth2_token_mock.return_value = {
            'email': 'google-user@example.com',
            'name': 'Google User',
            'email_verified': False,
        }

        with pytest.raises(AuthError, match='Token Google inválido'):
            GoogleOauthProvider().authenticate(Text.create('google-id-token'))
