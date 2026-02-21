from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.shared.responses.list_response import ListResponse
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos import UploadUrlDto
from equiny.core.storage.use_cases import GenerateUploadUrlsForHorseGalleryUseCase
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.providers_pipe import ProvidersPipe
from equiny.validation.shared.id_schema import IdSchema
from equiny.validation.shared.schema import Schema


class BodySchema(Schema):
    files_names: list[str]


class GenerateUploadUrlsForHorseGalleryController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/upload/horses/{horse_id}/gallery',
            status_code=HTTPStatus.CREATED,
            response_model=ListResponse[UploadUrlDto],
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            horse_id: IdSchema,
            body: BodySchema,
            file_storage_provider: FileStorageProvider = Depends(
                ProvidersPipe.get_file_storage_provider
            ),
        ) -> ListResponse[UploadUrlDto]:
            use_case = GenerateUploadUrlsForHorseGalleryUseCase(file_storage_provider)
            return use_case.execute(horse_id, body.files_names)
