from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends

from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.auth.domain.entities.dtos import SignUpResultDto
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.shared.interfaces.broker import Broker
from equiny.pipes import DatabasePipe, PubSubPipe, ProvidersPipe
from equiny.validation.shared import EmailSchema, NameSchema, Schema
from equiny.core.auth.use_cases.sign_up_account_use_case import SignUpAccountUseCase


class BodySchema(Schema):
    owner_name: NameSchema
    account_email: EmailSchema
    account_password: str


repository = Annotated[
    AccountsRepository, Depends(DatabasePipe.get_accounts_repository)
]
hash_provider = Annotated[HashProvider, Depends(ProvidersPipe.get_hash_provider)]
broker = Annotated[Broker, Depends(PubSubPipe.get_broker)]


class SignUpAccountController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/sign-up', status_code=HTTPStatus.CREATED, response_model=SignUpResultDto
        )
        def _(
            body: BodySchema,
            repository: repository,
            hash_provider: hash_provider,
            broker: broker,
        ) -> SignUpResultDto:
            use_case = SignUpAccountUseCase(
                repository=repository,
                hash_provider=hash_provider,
                broker=broker,
            )
            return use_case.execute(
                body.account_email,
                body.account_password,
                body.owner_name,
            )
