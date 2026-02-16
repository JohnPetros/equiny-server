from fastapi import APIRouter

from equiny.rest.controllers.profiling import (
    FetchOwnerController,
    FetchOwnerHorsesController,
)


class OwnersRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/owners')

        FetchOwnerController.handle(router)
        FetchOwnerHorsesController.handle(router)

        return router
