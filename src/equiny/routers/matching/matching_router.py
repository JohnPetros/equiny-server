from fastapi import APIRouter

from equiny.rest.controllers.matching import SwipeHorseController


class MatchingRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/matching', tags=['Matching module'])
        SwipeHorseController.handle(router)
        return router
