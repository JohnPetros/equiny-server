import pytest
from unittest.mock import Mock, create_autospec

from src.equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from src.equiny.core.storage.structures.dtos.upload_url_dto import UploadUrlDto
from src.equiny.core.storage.structures.upload_url import UploadUrl
from src.equiny.core.storage.use_cases.generate_upload_url_for_owner_avatar_use_case import (
    GenerateUploadUrlForOwnerAvatarUseCase,
)


class TestGenerateUploadUrlForOwnerAvatarUseCase:
    provider_mock: Mock
    use_case: GenerateUploadUrlForOwnerAvatarUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.provider_mock = create_autospec(FileStorageProvider, instance=True)
        self.use_case = GenerateUploadUrlForOwnerAvatarUseCase(
            provider=self.provider_mock
        )

    def test_should_return_upload_url_dto_when_owner_id_is_provided(self) -> None:
        owner_id = 'owner-1'
        file_name = 'avatar.jpg'
        upload_url = UploadUrl.create(
            UploadUrlDto(
                url='https://storage.local/avatar-upload',
                token='token-1',  # noqa: S106
                file_path='/profiling/owners/owner-1/avatar/randomized-avatar.jpg',
            )
        )
        self.provider_mock.generate_upload_url.return_value = upload_url

        result = self.use_case.execute(owner_id=owner_id, file_name=file_name)

        self.provider_mock.generate_upload_url.assert_called_once()
        file_path = self.provider_mock.generate_upload_url.call_args.args[0]
        assert file_path.value.startswith('/profiling/owners/owner-1/avatar/')
        assert file_path.value.endswith('avatar.jpg')
        assert result == upload_url.dto

    def test_should_raise_runtime_error_when_provider_fails_to_generate_upload_url(
        self,
    ) -> None:
        owner_id = 'owner-1'
        self.provider_mock.generate_upload_url.side_effect = RuntimeError(
            'provider unavailable'
        )

        with pytest.raises(RuntimeError, match='provider unavailable'):
            self.use_case.execute(owner_id=owner_id, file_name='avatar.jpg')

        self.provider_mock.generate_upload_url.assert_called_once()
