from fastapi import APIRouter

from equiny.rest.controllers.profiling import UploadImageFilesController


class StorageRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/storage', tags=['Storage module'])

        UploadImageFilesController.handle(router)

        return router
