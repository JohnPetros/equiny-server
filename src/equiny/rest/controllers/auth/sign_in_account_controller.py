from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends

from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.use_cases.sign_in_account_use_case import SignInAccountUseCase
from equiny.validation.shared import Schema, EmailSchema
from equiny.core.shared.interfaces.broker import Broker
from equiny.pipes import DatabasePipe, PubSubPipe, ProvidersPipe
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider


class BodySchema(Schema):
    email: EmailSchema
    password: str


class ResponseSchema(Schema):
    access_token: str


repository = Annotated[
    AccountsRepository, Depends(DatabasePipe.get_accounts_repository)
]
hash_provider = Annotated[HashProvider, Depends(ProvidersPipe.get_hash_provider)]
jwt_provider = Annotated[JwtProvider, Depends(ProvidersPipe.get_jwt_provider)]
broker = Annotated[Broker, Depends(PubSubPipe.get_broker)]


class SignInAccountController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/sign-in', status_code=HTTPStatus.CREATED, response_model=ResponseSchema
        )
        def _(
            body: BodySchema,
            repository: repository,
            hash_provider: hash_provider,
            jwt_provider: jwt_provider,
        ) -> ResponseSchema:
            use_case = SignInAccountUseCase(
                repository=repository,
                hash_provider=hash_provider,
                jwt_provider=jwt_provider,
            )
            access_token = use_case.execute(body.email, body.password)
            return ResponseSchema(access_token=access_token)
