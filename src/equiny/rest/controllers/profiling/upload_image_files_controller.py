from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.shared.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.use_cases import UploadImageFilesUseCase
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos import FileDto
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.providers_pipe import ProvidersPipe
from equiny.pipes.storage_pipe import StoragePipe


class UploadImageFilesController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/images/upload',
            status_code=HTTPStatus.CREATED,
            response_model=list[ImageDto],
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            files_dto: list[FileDto] = Depends(StoragePipe.get_image_files),
            file_storage_provider: FileStorageProvider = Depends(
                ProvidersPipe.get_file_storage_provider
            ),
        ) -> list[ImageDto]:
            use_case = UploadImageFilesUseCase(file_storage_provider)
            images = use_case.execute(files_dto)
            print('images', images)
            return images
