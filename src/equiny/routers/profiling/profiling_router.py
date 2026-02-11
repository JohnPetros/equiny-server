from fastapi import APIRouter

from equiny.routers.profiling.horses_router import HorsesRouter


class ProfilingRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/profiling', tags=['Profiling module'])

        router.include_router(HorsesRouter.register())

        return router
