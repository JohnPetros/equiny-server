from equiny.core.shared.domain.structures import Text
from equiny.core.shared.responses.list_response import ListResponse
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos import AttachmentDto, UploadUrlDto
from equiny.core.storage.structures.file_name import FileName


class GenerateUploadUrlsForAttachmentsUseCase:
    def __init__(
        self,
        provider: FileStorageProvider,
    ) -> None:
        self._provider = provider

    def execute(
        self, attachment_dtos: list[AttachmentDto]
    ) -> ListResponse[UploadUrlDto]:
        file_paths = [
            Text.create(
                f'/conversation/chats/{attachment_dto.chat_id}/messages/{attachment_dto.message_id}/attachments/{attachment_dto.attachment_id}/{attachment_dto.file_kind}/{FileName.create(attachment_dto.file_name).randomize.value}'
            )
            for attachment_dto in attachment_dtos
        ]
        upload_urls = self._provider.generate_upload_urls(file_paths)
        return ListResponse(items=[upload_url.dto for upload_url in upload_urls])
