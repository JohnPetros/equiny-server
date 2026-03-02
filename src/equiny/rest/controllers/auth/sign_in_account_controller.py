from http import HTTPStatus
from fastapi import APIRouter, Depends
from pydantic import AliasChoices, Field, BaseModel

from equiny.core.auth.domain.structures.dtos.jwt_dto import JwtDto
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.use_cases.sign_in_account_use_case import SignInAccountUseCase
from equiny.validation.shared import EmailSchema
from equiny.pipes import DatabasePipe, ProvidersPipe
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider


class BodySchema(BaseModel):
    email: EmailSchema = Field(validation_alias=AliasChoices('email', 'account_email'))
    password: str = Field(validation_alias=AliasChoices('password', 'account_password'))


class SignInAccountController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post('/sign-in', status_code=HTTPStatus.CREATED, response_model=JwtDto)
        def _(
            body: BodySchema,
            repository: AccountsRepository = Depends(
                DatabasePipe.get_accounts_repository
            ),
            hash_provider: HashProvider = Depends(ProvidersPipe.get_hash_provider),
            jwt_provider: JwtProvider = Depends(ProvidersPipe.get_jwt_provider),
        ) -> JwtDto:
            use_case = SignInAccountUseCase(
                repository=repository,
                hash_provider=hash_provider,
                jwt_provider=jwt_provider,
            )
            return use_case.execute(body.email, body.password)
