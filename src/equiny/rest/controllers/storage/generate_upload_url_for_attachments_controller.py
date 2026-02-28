from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.shared.responses.list_response import ListResponse
from equiny.core.storage.structures.dtos import AttachmentDto
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos import UploadUrlDto
from equiny.core.storage.use_cases.generate_upload_urls_for_attachments_use_case import (
    GenerateUploadUrlsForAttachmentsUseCase,
)
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
            use_case = GenerateUploadUrlsForAttachmentsUseCase(
                provider=file_storage_provider
            )
            return use_case.execute(attachment_dtos=body.attachments)
