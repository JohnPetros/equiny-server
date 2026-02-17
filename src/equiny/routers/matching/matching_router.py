from fastapi import APIRouter

from equiny.rest.controllers.matching import (
    DismatchHorseController,
    ListMatchesController,
    SwipeHorseController,
)


class MatchingRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/matching', tags=['Matching module'])
        DismatchHorseController.handle(router)
        ListMatchesController.handle(router)
        SwipeHorseController.handle(router)
        return router
