from fastapi import APIRouter

from equiny.rest.controllers.matching import (
    DismatchHorseController,
)


class MatchesRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/matches', tags=['Matches module'])

        DismatchHorseController.handle(router)

        return router
