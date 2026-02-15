from fastapi import APIRouter

from equiny.rest.controllers.profiling import (
    CreateHorseController,
    CreateHorseGalaryController,
    FetchHorseController,
)


class HorsesRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/horses')

        CreateHorseController.handle(router)
        CreateHorseGalaryController.handle(router)
        FetchHorseController.handle(router)

        return router
