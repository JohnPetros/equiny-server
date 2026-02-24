from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from equiny.constants import Env
from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.shared.domain.errors import AuthError


class JoseJwtProvider(JwtProvider):
    _ALGORITHM = 'HS256'
    _EXPIRATION_TIME_IN_MINUTES = 60

    def encode(self, subject: str) -> str:
        now_time = datetime.now(UTC)
        expiration_time = now_time + timedelta(minutes=self._EXPIRATION_TIME_IN_MINUTES)
        payload = {
            'sub': subject,
            'iat': now_time,
            'exp': expiration_time,
        }
        return jwt.encode(payload, Env.JWT_SECRET)

    def decode(self, token: str) -> dict[str, str]:
        try:
            decoded: dict[str, Any] = jwt.decode(
                token,
                Env.JWT_SECRET,
                algorithms=[self._ALGORITHM],
            )
        except JWTError as jwt_error:
            raise AuthError('JWT inválido') from jwt_error

        return {key: value for key, value in decoded.items() if isinstance(value, str)}
