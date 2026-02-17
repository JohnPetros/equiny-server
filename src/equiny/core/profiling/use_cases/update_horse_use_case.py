from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.errors import HorseNotFoundError
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.domain.structures.id import Id


class UpdateHorseUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self.repository = repository

    def execute(self, horse_id: str, owner_id: str, horse_dto: HorseDto) -> HorseDto:
        self._find_horse(Id.create(horse_id), Id.create(owner_id))
        horse_dto.id = horse_id
        horse = Horse.create(horse_dto)
        self.repository.replace(horse)
        return horse.dto

    def _find_horse(self, horse_id: Id, owner_id: Id) -> None:
        horse = self.repository.find_by_id_and_owner_id(horse_id, owner_id)
        if horse is None:
            raise HorseNotFoundError
