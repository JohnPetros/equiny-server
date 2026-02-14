from http import HTTPStatus
from fastapi import APIRouter

from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.use_cases.sign_in_account_use_case import SignInAccountUseCase
from equiny.validation.shared import Schema, EmailSchema


class BodySchema(Schema):
    email: EmailSchema
    password: str


class SignInAccountController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/sign-in', status_code=HTTPStatus.CREATED, response_model=AccountDto
        )
        def _(body: BodySchema) -> AccountDto:
            use_case = SignInAccountUseCase()
            return use_case.execute(body.email, body.password)
