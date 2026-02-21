import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.dtos.upload_url_dto import UploadUrlDto
from equiny.core.storage.structures.upload_url import UploadUrl
from equiny.core.storage.use_cases.generate_upload_urls_for_horser_gallery_use_case import (
    GenerateUploadUrlsForHorseGalleryUseCase,
)


class TestGenerateUploadUrlsForHorseGalleryUseCase:
    provider_mock: Mock
    use_case: GenerateUploadUrlsForHorseGalleryUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.provider_mock = create_autospec(FileStorageProvider, instance=True)
        self.use_case = GenerateUploadUrlsForHorseGalleryUseCase(
            provider=self.provider_mock
        )

    def test_should_return_upload_url_dtos_when_file_names_are_provided(self) -> None:
        horse_id = 'horse-1'
        file_names = ['gallery-1.jpg', 'gallery-2.png']
        upload_urls = [
            UploadUrl.create(
                UploadUrlDto(
                    url='https://storage.local/upload-1',
                    token='token-1',
                    file_path='/profiling/horses/horse-1/gallery/gallery-1.jpg',
                )
            ),
            UploadUrl.create(
                UploadUrlDto(
                    url='https://storage.local/upload-2',
                    token='token-2',
                    file_path='/profiling/horses/horse-1/gallery/gallery-2.png',
                )
            ),
        ]
        self.provider_mock.generate_upload_urls.return_value = upload_urls

        result = self.use_case.execute(horse_id=horse_id, file_names=file_names)

        self.provider_mock.generate_upload_urls.assert_called_once()
        file_paths = self.provider_mock.generate_upload_urls.call_args.args[0]
        assert file_paths[0].value.startswith('/profiling/horses/horse-1/gallery/')
        assert file_paths[0].value.endswith('gallery-1.jpg')
        assert file_paths[1].value.startswith('/profiling/horses/horse-1/gallery/')
        assert file_paths[1].value.endswith('gallery-2.png')
        assert result.items == [upload_urls[0].dto, upload_urls[1].dto]

    def test_should_raise_runtime_error_when_provider_fails_to_generate_upload_urls(
        self,
    ) -> None:
        horse_id = 'horse-1'
        file_names = ['gallery-1.jpg']
        self.provider_mock.generate_upload_urls.side_effect = RuntimeError(
            'provider unavailable'
        )

        with pytest.raises(RuntimeError, match='provider unavailable'):
            self.use_case.execute(horse_id=horse_id, file_names=file_names)

        self.provider_mock.generate_upload_urls.assert_called_once()
