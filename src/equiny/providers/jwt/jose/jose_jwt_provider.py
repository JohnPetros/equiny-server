from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt

from equiny.constants import Env
from equiny.core.auth.domain.structures.dtos.jwt_dto import JwtDto
from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.shared.domain.errors import AuthError


class JoseJwtProvider(JwtProvider):
    _ALGORITHM = 'HS256'
    _ACCESS_TOKEN_EXP_MINUTES = 60
    _REFRESH_TOKEN_EXP_DAYS = 30

    def encode(self, subject: str) -> JwtDto:
        access_token = self.encode_access_token(subject)
        refresh_token = self.encode_refresh_token(subject)
        return JwtDto(access_token=access_token, refresh_token=refresh_token)

    def encode_access_token(self, subject: str) -> str:
        now_time = datetime.now(UTC)
        expiration_time = now_time + timedelta(minutes=self._ACCESS_TOKEN_EXP_MINUTES)

        payload = {
            'sub': subject,
            'type': 'access',
            'iat': int(now_time.timestamp()),
            'exp': int(expiration_time.timestamp()),
        }

        return jwt.encode(payload, Env.JWT_SECRET, algorithm=self._ALGORITHM)

    def encode_refresh_token(self, subject: str) -> str:
        now_time = datetime.now(UTC)
        expiration_time = now_time + timedelta(days=self._REFRESH_TOKEN_EXP_DAYS)

        payload = {
            'sub': subject,
            'type': 'refresh',
            'jti': str(uuid4()),
            'iat': int(now_time.timestamp()),
            'exp': int(expiration_time.timestamp()),
        }

        return jwt.encode(payload, Env.JWT_SECRET, algorithm=self._ALGORITHM)

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
