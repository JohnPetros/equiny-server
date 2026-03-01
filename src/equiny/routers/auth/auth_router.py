from fastapi import APIRouter

from equiny.rest.controllers.auth import (
    ResendAccountVerificationEmailController,
    SignInAccountController,
    SignUpAccountController,
    VerifyAccountEmailController,
)


class AuthRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/auth', tags=['Auth module'])

        SignInAccountController.handle(router)
        SignUpAccountController.handle(router)
        VerifyAccountEmailController.handle(router)
        ResendAccountVerificationEmailController.handle(router)

        return router
