from fastapi import APIRouter

from equiny.rest.controllers.profiling import (
    CreateHorseController,
    CreateHorseGalleryController,
    FetchBreedsController,
    FetchHorseController,
    FetchHorseFeedController,
    FetchHorseGalleryController,
    ListHorseMatchesController,
    ViewHorseMatchController,
    UpdateHorseController,
    UpdateHorseGalleryController,
)


class HorsesRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/horses')

        CreateHorseController.handle(router)
        CreateHorseGalleryController.handle(router)
        FetchBreedsController.handle(router)
        UpdateHorseController.handle(router)
        UpdateHorseGalleryController.handle(router)
        FetchHorseController.handle(router)
        FetchHorseGalleryController.handle(router)
        FetchHorseFeedController.handle(router)
        ListHorseMatchesController.handle(router)
        ViewHorseMatchController.handle(router)

        return router
