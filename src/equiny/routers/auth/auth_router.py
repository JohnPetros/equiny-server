from fastapi import APIRouter

from equiny.rest.controllers.auth import (
    SignInAccountController,
    SignUpAccountController,
)


class AuthRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/auth', tags=['Auth module'])

        SignInAccountController.handle(router)
        SignUpAccountController.handle(router)

        return router
