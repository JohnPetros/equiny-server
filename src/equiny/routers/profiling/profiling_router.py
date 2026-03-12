from fastapi import APIRouter

from equiny.rest.controllers.profiling import GenerateIcebreakerController
from equiny.routers.profiling.horses_router import HorsesRouter
from equiny.routers.profiling.owners_router import OwnersRouter


class ProfilingRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/profiling', tags=['Profiling module'])

        GenerateIcebreakerController.handle(router)
        router.include_router(HorsesRouter.register())
        router.include_router(OwnersRouter.register())

        return router
