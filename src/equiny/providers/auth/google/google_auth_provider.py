from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token  # pyright: ignore[reportUnknownVariableType]

from equiny.constants import Env
from equiny.core.auth.interfaces.providers.google_auth_provider import (
    GoogleAuthProvider,
)
from equiny.core.shared.domain.errors import AuthError
from equiny.core.shared.domain.structures.text import Text


class GoogleOauthProvider(GoogleAuthProvider):
    def authenticate(self, id_token: Text) -> tuple[str, str]:
        try:
            payload: dict[str, Any] = dict(
                verify_oauth2_token(
                    id_token.value,
                    Request(),
                    Env.GOOGLE_OAUTH_CLIENT_ID,
                )
            )
        except Exception as error:
            raise AuthError('Token Google inválido') from error

        email = payload.get('email')
        name = payload.get('name')
        is_email_verified = payload.get('email_verified') is True

        if (
            not isinstance(email, str)
            or not isinstance(name, str)
            or not is_email_verified
        ):
            raise AuthError('Token Google inválido')

        return email, name
