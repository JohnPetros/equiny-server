import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.profiling.use_cases.upload_image_files_use_case import (
    UploadImageFilesUseCase,
)
from equiny.core.shared.domain.errors import ValidationError
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from tests.fakers.storage.structures.file_faker import FileFaker


class TestUploadImageFilesUseCase:
    file_storage_provider_mock: Mock
    use_case: UploadImageFilesUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.file_storage_provider_mock = create_autospec(
            FileStorageProvider, instance=True
        )
        self.use_case = UploadImageFilesUseCase(
            file_storage_provider=self.file_storage_provider_mock
        )

    def test_should_upload_image_files_and_return_image_dtos(self) -> None:
        files_dto = FileFaker.fake_many(count=2)
        keys = [Text.create('key-1'), Text.create('key-2')]
        self.file_storage_provider_mock.upload_many.return_value = keys

        result = self.use_case.execute(files_dto=files_dto)

        self.file_storage_provider_mock.upload_many.assert_called_once()
        assert len(result) == 2
        assert result[0].key == 'key-1'
        assert result[0].name == files_dto[0].name
        assert result[1].key == 'key-2'
        assert result[1].name == files_dto[1].name

    def test_should_raise_validation_error_when_files_list_is_empty(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            self.use_case.execute(files_dto=[])

        assert 'Pelo menos um arquivo deve ser enviado' in str(exc_info.value)
        self.file_storage_provider_mock.upload_many.assert_not_called()

    def test_should_raise_validation_error_when_file_is_not_an_image(self) -> None:
        files_dto = [
            FileFaker.fake_dto(name='document.pdf', content_type='application/pdf')
        ]

        with pytest.raises(ValidationError) as exc_info:
            self.use_case.execute(files_dto=files_dto)

        assert 'não é uma imagem válida' in str(exc_info.value)
        assert 'document.pdf' in str(exc_info.value)
        self.file_storage_provider_mock.upload_many.assert_not_called()

    def test_should_raise_validation_error_when_any_file_is_not_an_image(self) -> None:
        files_dto = [
            FileFaker.fake_dto(name='image.jpg', content_type='image/jpeg'),
            FileFaker.fake_dto(name='document.pdf', content_type='application/pdf'),
        ]

        with pytest.raises(ValidationError) as exc_info:
            self.use_case.execute(files_dto=files_dto)

        assert 'não é uma imagem válida' in str(exc_info.value)
        assert 'document.pdf' in str(exc_info.value)
        self.file_storage_provider_mock.upload_many.assert_not_called()
