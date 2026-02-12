from fastapi import Depends, Request

from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.shared.domain.errors.auth_error import AuthError
from equiny.pipes import ProvidersPipe


class AuthPipe:
    @staticmethod
    def verify_jwt(
        request: Request,
        jwt_provider: JwtProvider = Depends(ProvidersPipe.get_jwt_provider),
    ) -> dict[str, str]:
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            raise AuthError('Cabeçalho de autorização não encontrado')

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise AuthError('Authorization header inválido. Use: Bearer <token>')

        token = parts[1].strip()
        if not token:
            raise AuthError('Jwt não encontrado')

        return jwt_provider.decode(token)
