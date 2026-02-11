from fastapi import APIRouter

from equiny.rest.controllers.profiling import (
    CreateHorseController,
    FetchHorseController,
)


class HorsesRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/horses')

        CreateHorseController.handle(router)
        FetchHorseController.handle(router)

        return router
