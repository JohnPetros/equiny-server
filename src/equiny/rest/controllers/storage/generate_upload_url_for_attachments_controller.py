from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.shared.responses.list_response import ListResponse
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.structures.dtos import AttachmentDto
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos import UploadUrlDto
from equiny.core.storage.structures.file_name import FileName
from equiny.pipes.conversation_pipe import ConversationPipe
from equiny.pipes.providers_pipe import ProvidersPipe
from equiny.validation.shared import IdSchema, Schema


class BodySchema(Schema):
    attachments: list[AttachmentDto]


class GenerateUploadUrlsForAttachmentsController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/upload/chats/{chat_id}/messages/{message_id}/attachments',
            status_code=HTTPStatus.CREATED,
            response_model=ListResponse[UploadUrlDto],
        )
        def _(
            chat_id: IdSchema,
            message_id: IdSchema,
            body: BodySchema,
            *,
            _: None = Depends(ConversationPipe.verify_chat_participant),
            file_storage_provider: FileStorageProvider = Depends(
                ProvidersPipe.get_file_storage_provider
            ),
        ) -> ListResponse[UploadUrlDto]:
            attachments = [
                AttachmentDto(
                    kind=attachment.kind,
                    name=attachment.name,
                )
                for attachment in body.attachments
            ]
            files_paths = [
                Text.create(
                    f'conversation/chats/{chat_id}/messages/{message_id}/attachments/{attachment.kind}/{FileName.create(attachment.name).randomize.value}'
                )
                for attachment in attachments
            ]
            upload_urls = file_storage_provider.generate_upload_urls(files_paths)
            return ListResponse(items=[upload_url.dto for upload_url in upload_urls])
