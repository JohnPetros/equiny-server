from equiny.core.shared.domain.errors import ValidationError
from equiny.core.shared.domain.structures.dtos.image_dto import ImageDto
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.file import File
from equiny.core.storage.structures.dtos.file_dto import FileDto


class UploadImageFilesUseCase:
    def __init__(self, file_storage_provider: FileStorageProvider) -> None:
        self._file_storage_provider = file_storage_provider

    def execute(self, files_dto: list[FileDto]) -> list[ImageDto]:
        if len(files_dto) == 0:
            raise ValidationError('Pelo menos um arquivo deve ser enviado')

        images: list[ImageDto] = []
        for file_dto in files_dto:
            if not file_dto.content_type.startswith('image/'):
                raise ValidationError(f'{file_dto.name} não é uma imagem válida')

            file = File.create(file_dto)
            upload_url = self._file_storage_provider.generate_upload_url(
                Text.create(file.name.value)
            )
            uploaded_key = self._file_storage_provider.upload(file, upload_url)
            images.append(
                ImageDto(
                    key=uploaded_key.value,
                    name=file.name.value,
                )
            )

        return images
