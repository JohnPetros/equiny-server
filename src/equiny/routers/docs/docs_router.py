from fastapi import APIRouter

from equiny.rest.controllers.docs import (
    RenderDocsPageController,
)


class DocsRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/docs', include_in_schema=False)

        RenderDocsPageController.handle(router)

        return router
