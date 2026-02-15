from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.errors.horse_not_found_error import HorseNotFoundError
from equiny.core.profiling.domain.structures.dtos.gallery_dto import GalleryDto
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.interfaces.repositories.horsers_repository import (
    HorsesRepository,
)
from equiny.core.profiling.domain.structures.gallery import Gallery
from equiny.core.shared.domain.structures.id import Id


class CreateHorseGalleryUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self.repository = repository

    def execute(self, horse_id: str, images: list[ImageDto]) -> GalleryDto:
        horse = self._find_horse(Id.create(horse_id))
        gallery = Gallery.create(images)
        self.repository.add_many_images(horse.id, gallery.images)
        return gallery.dto

    def _find_horse(self, horse_id: Id) -> Horse:
        horse = self.repository.find_by_id(horse_id)
        if horse is None:
            raise HorseNotFoundError
        return horse
