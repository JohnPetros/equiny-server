from fastapi import APIRouter

from equiny.rest.controllers.matching import SwipeHorseController


class SwipesRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/swipes', tags=['Swipes module'])

        SwipeHorseController.handle(router)

        return router
