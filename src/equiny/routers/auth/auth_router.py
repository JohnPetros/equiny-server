from fastapi import APIRouter

from equiny.rest.controllers.auth import SignInAccountController


class AuthRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/auth', tags=['Auth module'])

        SignInAccountController.handle(router)

        return router
