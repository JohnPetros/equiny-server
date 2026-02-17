from fastapi import APIRouter

from equiny.rest.controllers.profiling import (
    FetchOwnerController,
    FetchOwnerHorsesController,
    UpdateOwnerController,
)


class OwnersRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/owners')

        FetchOwnerController.handle(router)
        FetchOwnerHorsesController.handle(router)
        UpdateOwnerController.handle(router)

        return router
