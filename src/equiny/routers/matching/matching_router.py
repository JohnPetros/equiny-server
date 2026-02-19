from fastapi import APIRouter

from equiny.routers.matching.swipes_router import SwipesRouter
from equiny.routers.matching.matches_router import MatchesRouter


class MatchingRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/matching', tags=['Matching module'])

        router.include_router(SwipesRouter.register())
        router.include_router(MatchesRouter.register())

        return router
