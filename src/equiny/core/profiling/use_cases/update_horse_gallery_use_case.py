from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.errors.horse_not_found_error import HorseNotFoundError
from equiny.core.profiling.domain.events.image_files_removed_event import (
    ImageFilesRemovedEvent,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.domain.structures.gallery import Gallery, GalleryDto
from equiny.core.auth.domain.errors import GalleryNotFoundError
from equiny.core.shared.interfaces.broker import Broker


class UpdateHorseGalleryUseCase:
    def __init__(self, repository: HorsesRepository, broker: Broker) -> None:
        self._repository = repository
        self._broker = broker

    def execute(
        self, owner_id: str, horse_id: str, gallery_dto: GalleryDto
    ) -> GalleryDto:
        horse = self._find_horse(Id.create(horse_id), Id.create(owner_id))
        gallery = Gallery.create(gallery_dto)
        old_gallery = self._find_gallery(horse.id)
        removed_images = gallery.get_removed_images(old_gallery)

        self._repository.delete_many_images(horse.id)
        self._repository.add_many_images(horse.id, gallery.images)

        if removed_images:
            event = ImageFilesRemovedEvent(
                [image.key.value for image in removed_images]
            )
            self._broker.publish(event)

        return gallery.dto

    def _find_gallery(self, horse_id: Id) -> Gallery:
        gallery = self._repository.find_gallery_by_horse_id(horse_id)
        if gallery is None:
            raise GalleryNotFoundError
        return gallery

    def _find_horse(self, horse_id: Id, owner_id: Id) -> Horse:
        horse = self._repository.find_by_id_and_owner_id(horse_id, owner_id)
        if horse is None:
            raise HorseNotFoundError
        return horse
