from unittest.mock import Mock, create_autospec

import pytest

from equiny.core.auth.domain.errors import GalleryNotFoundError
from equiny.core.profiling.domain.errors import HorseNotFoundError
from equiny.core.profiling.domain.structures.dtos.gallery_dto import GalleryDto
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.domain.structures.gallery import Gallery
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.get_horse_gallery import GetHorseGalleryUseCase
from tests.fakers.profiling.entities.horses_faker import HorsesFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestGetHorseGalleryUseCase:
    repository_mock: Mock
    use_case: GetHorseGalleryUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(HorsesRepository, instance=True)
        self.use_case = GetHorseGalleryUseCase(repository=self.repository_mock)

    def test_should_return_gallery_dto_when_horse_and_gallery_exist(self) -> None:
        horse = HorsesFaker.fake()
        gallery_dto = GalleryDto(
            images=[
                ImageDto(key='image-key-1', name='cover.jpg'),
                ImageDto(key='image-key-2', name='profile.jpg'),
            ]
        )
        gallery = Gallery.create(gallery_dto)
        owner_id = IdFaker.fake().value
        self.repository_mock.find_by_id_and_owner_id.return_value = horse
        self.repository_mock.find_gallery_by_horse_id.return_value = gallery

        result = self.use_case.execute(owner_id=owner_id, horse_id=horse.id.value)

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.repository_mock.find_gallery_by_horse_id.assert_called_once_with(horse.id)

        searched_horse_id = self.repository_mock.find_by_id_and_owner_id.call_args[0][0]
        searched_owner_id = self.repository_mock.find_by_id_and_owner_id.call_args[0][1]

        assert searched_horse_id == horse.id
        assert searched_owner_id.value == owner_id
        assert result == gallery_dto

    def test_should_raise_horse_not_found_error_when_horse_does_not_exist(self) -> None:
        owner_id = IdFaker.fake().value
        horse_id = IdFaker.fake().value
        self.repository_mock.find_by_id_and_owner_id.return_value = None

        with pytest.raises(HorseNotFoundError):
            self.use_case.execute(owner_id=owner_id, horse_id=horse_id)

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.repository_mock.find_gallery_by_horse_id.assert_not_called()

    def test_should_raise_gallery_not_found_error_when_gallery_does_not_exist(
        self,
    ) -> None:
        horse = HorsesFaker.fake()
        owner_id = IdFaker.fake().value
        self.repository_mock.find_by_id_and_owner_id.return_value = horse
        self.repository_mock.find_gallery_by_horse_id.return_value = None

        with pytest.raises(GalleryNotFoundError):
            self.use_case.execute(owner_id=owner_id, horse_id=horse.id.value)

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.repository_mock.find_gallery_by_horse_id.assert_called_once_with(horse.id)
