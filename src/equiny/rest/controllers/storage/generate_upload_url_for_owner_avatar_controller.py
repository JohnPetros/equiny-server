from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos import UploadUrlDto
from equiny.core.storage.use_cases import GenerateUploadUrlForOwnerAvatarUseCase
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.providers_pipe import ProvidersPipe
from equiny.validation.shared.id_schema import IdSchema
from equiny.validation.shared.schema import Schema


class BodySchema(Schema):
    file_name: str


class GenerateUploadUrlForOwnerAvatarController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/upload/owners/{owner_id}/avatar',
            status_code=HTTPStatus.CREATED,
            response_model=UploadUrlDto,
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            owner_id: IdSchema,
            body: BodySchema,
            file_storage_provider: FileStorageProvider = Depends(
                ProvidersPipe.get_file_storage_provider
            ),
        ) -> UploadUrlDto:
            use_case = GenerateUploadUrlForOwnerAvatarUseCase(file_storage_provider)
            return use_case.execute(owner_id, body.file_name)
