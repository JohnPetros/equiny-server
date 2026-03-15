from unittest.mock import Mock, create_autospec

import pytest

from src.equiny.core.auth.domain.errors import GalleryNotFoundError
from src.equiny.core.profiling.domain.errors import HorseNotFoundError
from src.equiny.core.profiling.domain.events.image_files_removed_event import (
    ImagesFilesRemovedEvent,
)
from src.equiny.core.profiling.domain.structures.dtos.gallery_dto import GalleryDto
from src.equiny.core.shared.domain.structures.dtos.image_dto import ImageDto
from src.equiny.core.profiling.domain.structures.gallery import Gallery
from src.equiny.core.profiling.interfaces.repositories import HorsesRepository
from src.equiny.core.profiling.use_cases.update_horse_gallery_use_case import (
    UpdateHorseGalleryUseCase,
)
from src.equiny.core.shared.interfaces.broker import Broker
from tests.fakers.profiling.entities.horses_faker import HorsesFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestUpdateHorseGalleryUseCase:
    repository_mock: Mock
    broker_mock: Mock
    use_case: UpdateHorseGalleryUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(HorsesRepository, instance=True)
        self.broker_mock = create_autospec(Broker, instance=True)
        self.use_case = UpdateHorseGalleryUseCase(
            repository=self.repository_mock,
            broker=self.broker_mock,
        )

    def test_should_update_gallery_and_publish_event_when_images_are_removed(
        self,
    ) -> None:
        horse = HorsesFaker.fake()
        owner_id = IdFaker.fake().value
        old_gallery = Gallery.create(
            GalleryDto(
                images=[
                    ImageDto(key='image-key-1', name='cover.jpg'),
                    ImageDto(key='image-key-2', name='profile.jpg'),
                ]
            )
        )
        new_gallery_dto = GalleryDto(
            images=[ImageDto(key='image-key-1', name='cover.jpg')]
        )
        self.repository_mock.find_by_id_and_owner_id.return_value = horse
        self.repository_mock.find_gallery_by_horse_id.return_value = old_gallery

        result = self.use_case.execute(
            owner_id=owner_id,
            horse_id=horse.id.value,
            gallery_dto=new_gallery_dto,
        )

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.repository_mock.find_gallery_by_horse_id.assert_called_once_with(horse.id)
        self.repository_mock.delete_many_images.assert_called_once_with(horse.id)
        self.repository_mock.add_many_images.assert_called_once()
        self.broker_mock.publish.assert_called_once()

        searched_horse_id = self.repository_mock.find_by_id_and_owner_id.call_args[0][0]
        searched_owner_id = self.repository_mock.find_by_id_and_owner_id.call_args[0][1]
        saved_horse_id, saved_images = self.repository_mock.add_many_images.call_args[0]
        published_event = self.broker_mock.publish.call_args[0][0]

        assert searched_horse_id == horse.id
        assert searched_owner_id.value == owner_id
        assert saved_horse_id == horse.id
        assert [image.dto for image in saved_images] == new_gallery_dto.images
        assert result == new_gallery_dto
        assert isinstance(published_event, ImagesFilesRemovedEvent)
        assert published_event.payload.image_files_keys == ['image-key-2']

    def test_should_update_gallery_without_publishing_event_when_no_images_are_removed(
        self,
    ) -> None:
        horse = HorsesFaker.fake()
        owner_id = IdFaker.fake().value
        gallery_dto = GalleryDto(images=[ImageDto(key='image-key-1', name='cover.jpg')])
        old_gallery = Gallery.create(gallery_dto)
        self.repository_mock.find_by_id_and_owner_id.return_value = horse
        self.repository_mock.find_gallery_by_horse_id.return_value = old_gallery

        result = self.use_case.execute(
            owner_id=owner_id,
            horse_id=horse.id.value,
            gallery_dto=gallery_dto,
        )

        self.repository_mock.delete_many_images.assert_called_once_with(horse.id)
        self.repository_mock.add_many_images.assert_called_once()
        self.broker_mock.publish.assert_not_called()
        assert result == gallery_dto

    def test_should_raise_horse_not_found_error_when_horse_does_not_exist(self) -> None:
        owner_id = IdFaker.fake().value
        horse_id = IdFaker.fake().value
        gallery_dto = GalleryDto(images=[ImageDto(key='image-key-1', name='cover.jpg')])
        self.repository_mock.find_by_id_and_owner_id.return_value = None

        with pytest.raises(HorseNotFoundError):
            self.use_case.execute(
                owner_id=owner_id,
                horse_id=horse_id,
                gallery_dto=gallery_dto,
            )

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.repository_mock.find_gallery_by_horse_id.assert_not_called()
        self.repository_mock.delete_many_images.assert_not_called()
        self.repository_mock.add_many_images.assert_not_called()
        self.broker_mock.publish.assert_not_called()

    def test_should_raise_gallery_not_found_error_when_gallery_does_not_exist(
        self,
    ) -> None:
        horse = HorsesFaker.fake()
        owner_id = IdFaker.fake().value
        gallery_dto = GalleryDto(images=[ImageDto(key='image-key-1', name='cover.jpg')])
        self.repository_mock.find_by_id_and_owner_id.return_value = horse
        self.repository_mock.find_gallery_by_horse_id.return_value = None

        with pytest.raises(GalleryNotFoundError):
            self.use_case.execute(
                owner_id=owner_id,
                horse_id=horse.id.value,
                gallery_dto=gallery_dto,
            )

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.repository_mock.find_gallery_by_horse_id.assert_called_once_with(horse.id)
        self.repository_mock.delete_many_images.assert_not_called()
        self.repository_mock.add_many_images.assert_not_called()
        self.broker_mock.publish.assert_not_called()
