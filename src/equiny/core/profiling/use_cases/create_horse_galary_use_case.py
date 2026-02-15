from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.errors.horse_not_found_error import HorseNotFoundError
from equiny.core.profiling.domain.structures.dtos.galary_dto import GalaryDto
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.interfaces.repositories.horsers_repository import (
    HorsesRepository,
)
from equiny.core.profiling.domain.structures.galery import Galery
from equiny.core.shared.domain.structures.id import Id


class CreateHorseGalaryUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self.repository = repository

    def execute(self, horse_id: str, images: list[ImageDto]) -> GalaryDto:
        horse = self._find_horse(Id.create(horse_id))
        galery = Galery.create(images)
        self.repository.add_many_images(horse.id, galery.images)
        return galery.dto

    def _find_horse(self, horse_id: Id) -> Horse:
        horse = self.repository.find_by_id(horse_id)
        if horse is None:
            raise HorseNotFoundError
        return horse
