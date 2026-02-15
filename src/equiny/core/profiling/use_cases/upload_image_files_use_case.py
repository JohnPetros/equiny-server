from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos import FileDto
from equiny.core.storage.structures.file import File
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.shared.domain.errors import ValidationError


class UploadImageFilesUseCase:
    def __init__(self, file_storage_provider: FileStorageProvider) -> None:
        self.file_storage_provider = file_storage_provider

    def execute(self, files_dto: list[FileDto]) -> list[ImageDto]:
        if not files_dto:
            raise ValidationError('Pelo menos um arquivo deve ser enviado')

        files: list[File] = []
        for dto in files_dto:
            if not dto.content_type.startswith('image/'):
                raise ValidationError(
                    f'O arquivo "{dto.name}" não é uma imagem válida. '
                    'Apenas arquivos de imagem são aceitos.'
                )
            files.append(File.create(dto))

        keys = self.file_storage_provider.upload_many(files)

        return [
            ImageDto(key=key.value, name=file_dto.name)
            for key, file_dto in zip(keys, files_dto, strict=True)
        ]
