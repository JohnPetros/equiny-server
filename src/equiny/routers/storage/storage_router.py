from fastapi import APIRouter

from equiny.rest.controllers.storage import (
    GenerateUploadUrlForOwnerAvatarController,
    GenerateUploadUrlsForAttachmentsController,
    GenerateUploadUrlsForHorseGalleryController,
)


class StorageRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/storage', tags=['Storage module'])

        GenerateUploadUrlForOwnerAvatarController.handle(router)
        GenerateUploadUrlsForAttachmentsController.handle(router)
        GenerateUploadUrlsForHorseGalleryController.handle(router)

        return router
