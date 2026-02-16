from fastapi import APIRouter

from equiny.rest.controllers.profiling import (
    CreateHorseController,
    CreateHorseGalleryController,
    FetchHorseController,
    FetchHorseGalleryController,
    ToggleHorseActivationController,
    UpdateHorseController,
    UpdateHorseGalleryController,
)


class HorsesRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/horses')

        CreateHorseController.handle(router)
        CreateHorseGalleryController.handle(router)
        UpdateHorseController.handle(router)
        UpdateHorseGalleryController.handle(router)
        ToggleHorseActivationController.handle(router)
        FetchHorseController.handle(router)
        FetchHorseGalleryController.handle(router)

        return router
