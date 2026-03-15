from http import HTTPStatus

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from equiny.core.auth.domain.structures.dtos.jwt_dto import JwtDto
from equiny.core.auth.interfaces.providers import GoogleAuthProvider, JwtProvider
from equiny.core.auth.interfaces.repositories import AccountsRepository
from equiny.core.auth.use_cases import SignUpWithGoogleUseCase
from equiny.core.shared.interfaces import Broker
from equiny.pipes import DatabasePipe, ProvidersPipe, PubSubPipe


class _BodySchema(BaseModel):
    id_token: str


class SignUpWithGoogleController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/sign-up/google',
            status_code=HTTPStatus.CREATED,
            response_model=JwtDto,
        )
        def _(
            body: _BodySchema,
            repository: AccountsRepository = Depends(
                DatabasePipe.get_accounts_repository
            ),
            google_auth_provider: GoogleAuthProvider = Depends(
                ProvidersPipe.get_google_auth_provider
            ),
            jwt_provider: JwtProvider = Depends(ProvidersPipe.get_jwt_provider),
            broker: Broker = Depends(PubSubPipe.get_broker_from_request),
        ) -> JwtDto:
            use_case = SignUpWithGoogleUseCase(
                repository=repository,
                google_auth_provider=google_auth_provider,
                jwt_provider=jwt_provider,
                broker=broker,
            )
            return use_case.execute(body.id_token)
