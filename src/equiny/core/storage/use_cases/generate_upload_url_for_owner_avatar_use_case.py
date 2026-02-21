from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos.upload_url_dto import UploadUrlDto
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.structures.file_name import FileName


class GenerateUploadUrlForOwnerAvatarUseCase:
    def __init__(self, provider: FileStorageProvider) -> None:
        self._provider = provider

    def execute(self, owner_id: str, file_name: str) -> UploadUrlDto:
        file_path = Text.create(
            f'profiling/owners/{owner_id}/avatar/{FileName.create(file_name).randomize.value}'
        )
        upload_url = self._provider.generate_upload_url(file_path)
        return upload_url.dto
