from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.domain.errors.horse_not_found_error import HorseNotFoundError
from equiny.core.profiling.domain.structures.gallery import Gallery, GalleryDto
from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.auth.domain.errors import GalleryNotFoundError


class GetHorseGalleryUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self.repository = repository

    def execute(self, owner_id: str, horse_id: str) -> GalleryDto:
        horse = self._find_horse(Id.create(owner_id), Id.create(horse_id))
        gallery = self._find_gallery(horse.id)
        return gallery.dto

    def _find_horse(self, owner_id: Id, horse_id: Id) -> Horse:
        horse = self.repository.find_by_id_and_owner_id(horse_id, owner_id)
        if horse is None:
            raise HorseNotFoundError
        return horse

    def _find_gallery(self, horse_id: Id) -> Gallery:
        gallery = self.repository.find_gallery_by_horse_id(horse_id)
        if gallery is None:
            raise GalleryNotFoundError
        return gallery
