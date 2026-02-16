from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.errors.horse_not_found_error import HorseNotFoundError
from equiny.core.profiling.interfaces.repositories.horsers_repository import (
    HorsesRepository,
)
from equiny.core.shared.domain.structures.id import Id


class ToggleHorseActivationUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self._repository = repository

    def execute(self, horse_id: str, owner_id: str) -> HorseDto:
        horse = self._find_horse(Id.create(owner_id), Id.create(horse_id))
        horse.toggle_activation()
        self._repository.replace(horse)
        return horse.dto

    def _find_horse(self, owner_id: Id, horse_id: Id) -> Horse:
        horse = self._repository.find_by_id_and_owner_id(horse_id, owner_id)
        if horse is None:
            raise HorseNotFoundError
        return horse
