import pytest
from unittest.mock import Mock, create_autospec

from equiny.core.profiling.domain.errors import HorseNotFoundError
from equiny.core.shared.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.interfaces.repositories import (
    HorsesRepository,
    OwnersRepository,
)
from equiny.core.profiling.use_cases.create_horse_gallery_use_case import (
    CreateHorseGalleryUseCase,
)
from tests.fakers.profiling.entities.horses_faker import HorsesFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestCreateHorseGalleryUseCase:
    horses_repository_mock: Mock
    owners_repository_mock: Mock
    use_case: CreateHorseGalleryUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.horses_repository_mock = create_autospec(HorsesRepository, instance=True)
        self.owners_repository_mock = create_autospec(OwnersRepository, instance=True)
        self.use_case = CreateHorseGalleryUseCase(
            self.horses_repository_mock,
            self.owners_repository_mock,
        )

    def test_should_create_gallery_and_add_images_to_repository_when_horse_exists(
        self,
    ) -> None:
        horse = HorsesFaker.fake()
        owner_id = IdFaker.fake().value
        images = [
            ImageDto(key='image-key-1', name='cover.jpg'),
            ImageDto(key='image-key-2', name='profile.jpg'),
        ]
        self.horses_repository_mock.find_by_id_and_owner_id.return_value = horse

        result = self.use_case.execute(
            horse_id=horse.id.value,
            owner_id=owner_id,
            images=images,
        )

        self.horses_repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.horses_repository_mock.add_many_images.assert_called_once()
        self.owners_repository_mock.update_has_completed_onboarding.assert_called_once()

        searched_horse_id = (
            self.horses_repository_mock.find_by_id_and_owner_id.call_args[0][0]
        )
        searched_owner_id = (
            self.horses_repository_mock.find_by_id_and_owner_id.call_args[0][1]
        )
        saved_horse_id, saved_images = (
            self.horses_repository_mock.add_many_images.call_args[0]
        )

        assert searched_horse_id == horse.id
        assert searched_owner_id.value == owner_id
        assert saved_horse_id == horse.id
        assert [image.dto for image in saved_images] == images
        assert result.images == images

    def test_should_raise_horse_not_found_error_when_horse_does_not_exist(self) -> None:
        horse_id = IdFaker.fake().value
        owner_id = IdFaker.fake().value
        images = [ImageDto(key='image-key-1', name='cover.jpg')]
        self.horses_repository_mock.find_by_id_and_owner_id.return_value = None

        with pytest.raises(HorseNotFoundError):
            self.use_case.execute(horse_id=horse_id, owner_id=owner_id, images=images)

        self.horses_repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.horses_repository_mock.add_many_images.assert_not_called()
        self.owners_repository_mock.update_has_completed_onboarding.assert_not_called()

    def test_should_raise_horse_not_found_error_when_horse_does_not_belong_to_owner(
        self,
    ) -> None:
        horse_id = IdFaker.fake().value
        owner_id = IdFaker.fake().value
        images = [ImageDto(key='image-key-1', name='cover.jpg')]
        self.horses_repository_mock.find_by_id_and_owner_id.return_value = None

        with pytest.raises(HorseNotFoundError):
            self.use_case.execute(horse_id=horse_id, owner_id=owner_id, images=images)

        self.horses_repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.horses_repository_mock.add_many_images.assert_not_called()
        self.owners_repository_mock.update_has_completed_onboarding.assert_not_called()
