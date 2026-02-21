from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.shared.responses.list_response import ListResponse
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.structures.dtos import AttachmentDto
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos import UploadUrlDto
from equiny.core.storage.structures.file_kind import FileKind
from equiny.core.storage.structures.file_name import FileName
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.conversation_pipe import ConversationPipe
from equiny.pipes.providers_pipe import ProvidersPipe
from equiny.validation.shared import IdSchema, Schema


class BodySchema(Schema):
    files_names: list[str]


class GenerateUploadUrlsForAttachmentsController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/upload/chats/{chat_id}/messages/{message_id}/attachments/{attachment_id}/images',
            status_code=HTTPStatus.CREATED,
            response_model=ListResponse[UploadUrlDto],
            dependencies=[Depends(AuthPipe.verify_jwt)],
        )
        def _(
            chat_id: IdSchema,
            message_id: IdSchema,
            attachment_id: IdSchema,
            body: BodySchema,
            *,
            _: None = Depends(ConversationPipe.verify_chat_participant),
            file_storage_provider: FileStorageProvider = Depends(
                ProvidersPipe.get_file_storage_provider
            ),
        ) -> ListResponse[UploadUrlDto]:
            attachments = [
                AttachmentDto(
                    chat_id=chat_id,
                    message_id=message_id,
                    attachment_id=attachment_id,
                    file_kind=FileKind.create_as_images().dto,
                    file_name=file_name,
                )
                for file_name in body.files_names
            ]
            files_paths = [
                Text.create(
                    f'conversation/chats/{attachment.chat_id}/messages/{attachment.message_id}/attachments/{attachment.attachment_id}/{attachment.file_kind}/{FileName.create(attachment.file_name).randomize.value}'
                )
                for attachment in attachments
            ]
            upload_urls = file_storage_provider.generate_upload_urls(files_paths)
            return ListResponse(items=[upload_url.dto for upload_url in upload_urls])
