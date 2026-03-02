from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.shared.domain.errors.auth_error import AuthError
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.pipes.providers_pipe import ProvidersPipe
from equiny.pipes.database_pipe import DatabasePipe

bearer_scheme = HTTPBearer(auto_error=False)


class AuthPipe:
    @staticmethod
    def verify_jwt(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        jwt_provider: JwtProvider = Depends(ProvidersPipe.get_jwt_provider),
        accounts_repository: AccountsRepository = Depends(
            DatabasePipe.get_accounts_repository
        ),
    ) -> dict[str, str]:
        if credentials is None:
            raise AuthError('Cabeçalho de autorização não encontrado')

        if credentials.scheme.lower() != 'bearer':
            raise AuthError('Autorização inválida. Use: Bearer <token>')

        token = (credentials.credentials or '').strip()
        if not token:
            raise AuthError('Jwt não encontrado')

        jwt = jwt_provider.decode(token)
        account = accounts_repository.find_by_id(Id.create(jwt['sub']))
        if account is None:
            raise AuthError('Conta não encontrada')
        if not account.is_verified:
            raise AuthError('Conta não verificada')
        return jwt

    @staticmethod
    def verify_jwt_from_query(
        token: str,
        jwt_provider: JwtProvider = Depends(ProvidersPipe.get_jwt_provider),
    ) -> dict[str, str]:
        return jwt_provider.decode(token)
