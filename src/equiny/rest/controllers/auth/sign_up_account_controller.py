from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.shared.interfaces.broker import Broker
from equiny.pipes import DatabasePipe, PubSubPipe, ProvidersPipe
from equiny.validation.shared import EmailSchema, NameSchema, Schema
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.use_cases.sign_up_account_use_case import SignUpAccountUseCase


class BodySchema(Schema):
    owner_name: NameSchema
    account_email: EmailSchema
    account_password: str


class SignUpAccountController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/sign-up', status_code=HTTPStatus.CREATED, response_model=AccountDto
        )
        async def _(
            body: BodySchema,
            repository: AccountsRepository = Depends(
                DatabasePipe.get_accounts_repository
            ),
            hash_provider: HashProvider = Depends(ProvidersPipe.get_hash_provider),
            jwt_provider: JwtProvider = Depends(ProvidersPipe.get_jwt_provider),
            broker: Broker = Depends(PubSubPipe.get_broker),
        ) -> AccountDto:
            use_case = SignUpAccountUseCase(
                repository=repository,
                hash_provider=hash_provider,
                jwt_provider=jwt_provider,
                broker=broker,
            )
            return use_case.execute(
                body.owner_name,
                body.account_email,
                body.account_password,
            )
