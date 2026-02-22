from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.shared.domain.errors.auth_error import AuthError
from equiny.pipes.providers_pipe import ProvidersPipe

bearer_scheme = HTTPBearer(auto_error=False)


class AuthPipe:
    @staticmethod
    def verify_jwt(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        jwt_provider: JwtProvider = Depends(ProvidersPipe.get_jwt_provider),
    ) -> dict[str, str]:
        if credentials is None:
            raise AuthError('Cabeçalho de autorização não encontrado')

        if credentials.scheme.lower() != 'bearer':
            raise AuthError('Autorização inválida. Use: Bearer <token>')

        token = (credentials.credentials or '').strip()
        if not token:
            raise AuthError('Jwt não encontrado')

        return jwt_provider.decode(token)

    @staticmethod
    def verify_jwt_from_query(
        token: str,
        jwt_provider: JwtProvider = Depends(ProvidersPipe.get_jwt_provider),
    ) -> dict[str, str]:
        return jwt_provider.decode(token)
