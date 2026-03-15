import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos import AttachmentDto, UploadUrlDto
from equiny.core.storage.structures.upload_url import UploadUrl
from equiny.core.storage.use_cases.generate_upload_urls_for_attachments_use_case import (
    GenerateUploadUrlsForAttachmentsUseCase,
)


class TestGenerateUploadUrlsForAttachmentsUseCase:
    provider_mock: Mock
    use_case: GenerateUploadUrlsForAttachmentsUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.provider_mock = create_autospec(FileStorageProvider, instance=True)
        self.use_case = GenerateUploadUrlsForAttachmentsUseCase(
            provider=self.provider_mock
        )

    def test_should_return_upload_url_dtos_when_attachment_dtos_are_valid(self) -> None:
        attachment_dtos = [
            AttachmentDto(
                chat_id='chat-1',
                message_id='message-1',
                attachment_id='attachment-1',
                file_kind='images',
                file_name='image-1.jpg',
            ),
            AttachmentDto(
                chat_id='chat-2',
                message_id='message-2',
                attachment_id='attachment-2',
                file_kind='videos',
                file_name='video-1.mp4',
            ),
        ]
        upload_urls = [
            UploadUrl.create(
                UploadUrlDto(
                    url='https://storage.local/upload-1',
                    token='token-1',  # noqa: S106
                    file_path='/conversation/chats/chat-1/messages/message-1/attachments/attachment-1/images/image-1.jpg',
                )
            ),
            UploadUrl.create(
                UploadUrlDto(
                    url='https://storage.local/upload-2',
                    token='token-2',  # noqa: S106
                    file_path='/conversation/chats/chat-2/messages/message-2/attachments/attachment-2/videos/video-1.mp4',
                )
            ),
        ]
        self.provider_mock.generate_upload_urls.return_value = upload_urls

        result = self.use_case.execute(attachment_dtos=attachment_dtos)

        self.provider_mock.generate_upload_urls.assert_called_once()
        file_paths = self.provider_mock.generate_upload_urls.call_args.args[0]
        assert file_paths[0].value.startswith(
            '/conversation/chats/chat-1/messages/message-1/attachments/attachment-1/images/'
        )
        assert file_paths[0].value.endswith('image-1.jpg')
        assert file_paths[1].value.startswith(
            '/conversation/chats/chat-2/messages/message-2/attachments/attachment-2/videos/'
        )
        assert file_paths[1].value.endswith('video-1.mp4')
        assert result.items == [upload_urls[0].dto, upload_urls[1].dto]

    def test_should_raise_runtime_error_when_provider_fails_to_generate_upload_urls(
        self,
    ) -> None:
        attachment_dtos = [
            AttachmentDto(
                chat_id='chat-1',
                message_id='message-1',
                attachment_id='attachment-1',
                file_kind='images',
                file_name='image-1.jpg',
            )
        ]
        self.provider_mock.generate_upload_urls.side_effect = RuntimeError(
            'provider unavailable'
        )

        with pytest.raises(RuntimeError, match='provider unavailable'):
            self.use_case.execute(attachment_dtos=attachment_dtos)

        self.provider_mock.generate_upload_urls.assert_called_once()
