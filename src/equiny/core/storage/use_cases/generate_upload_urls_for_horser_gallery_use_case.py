from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.shared.responses.list_response import ListResponse
from equiny.core.storage.structures.dtos.upload_url_dto import UploadUrlDto
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.structures.file_name import FileName


class GenerateUploadUrlsForHorseGalleryUseCase:
    def __init__(self, provider: FileStorageProvider) -> None:
        self._provider = provider

    def execute(
        self, horse_id: str, file_names: list[str]
    ) -> ListResponse[UploadUrlDto]:
        file_paths: list[Text] = []
        for file_name in file_names:
            file_paths.append(
                Text.create(
                    f'/profiling/horses/{horse_id}/gallery/{FileName.create(file_name).randomize.value}'
                )
            )
        upload_urls = self._provider.generate_upload_urls(file_paths)
        return ListResponse(items=[upload_url.dto for upload_url in upload_urls])
