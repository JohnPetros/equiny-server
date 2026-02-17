from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.errors.horse_not_found_error import HorseNotFoundError
from equiny.core.profiling.domain.structures.dtos.gallery_dto import GalleryDto
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.interfaces.repositories.horsers_repository import (
    HorsesRepository,
)
from equiny.core.profiling.domain.structures.gallery import Gallery
from equiny.core.profiling.interfaces.repositories.owners_repository import (
    OwnersRepository,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.logical import Logical


class CreateHorseGalleryUseCase:
    def __init__(
        self, horsers_repository: HorsesRepository, owners_repository: OwnersRepository
    ) -> None:
        self.horsers_repository = horsers_repository
        self.owners_repository = owners_repository

    def execute(
        self,
        horse_id: str,
        owner_id: str,
        gallery_dto: GalleryDto | None = None,
        images: list[ImageDto] | None = None,
    ) -> GalleryDto:
        horse = self._find_horse(Id.create(horse_id), Id.create(owner_id))
        if gallery_dto is None:
            gallery_dto = GalleryDto(images=images or [])
        gallery = Gallery.create(gallery_dto)
        self.horsers_repository.add_many_images(horse.id, gallery.images)
        self.owners_repository.update_has_completed_onboarding(
            Id.create(owner_id), Logical.create_true()
        )
        return gallery.dto

    def _find_horse(self, horse_id: Id, owner_id: Id) -> Horse:
        horse = self.horsers_repository.find_by_id_and_owner_id(horse_id, owner_id)
        if horse is None:
            raise HorseNotFoundError
        return horse
