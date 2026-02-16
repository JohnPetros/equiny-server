from typing import Annotated
from fastapi import File, UploadFile
from fastapi.exceptions import HTTPException
from http import HTTPStatus

from equiny.core.storage.structures.dtos import FileDto


class StoragePipe:
    @staticmethod
    def get_image_files(
        files: Annotated[list[UploadFile], File(min_length=1)],
    ) -> list[FileDto]:
        for uploaded_file in files:
            content_type = uploaded_file.content_type or 'application/octet-stream'
            if not content_type.startswith('image/'):
                raise HTTPException(
                    status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                    detail=(
                        f'O arquivo "{uploaded_file.filename or "unnamed"}" não é uma imagem. '
                        'Apenas arquivos de imagem (ex: JPEG, PNG, GIF, WebP) são aceitos.'
                    ),
                )

        return [
            FileDto(
                name=uploaded_file.filename or 'unnamed',
                folder='images',
                data=uploaded_file.file.read(),
                content_type=uploaded_file.content_type or 'application/octet-stream',
            )
            for uploaded_file in files
        ]
