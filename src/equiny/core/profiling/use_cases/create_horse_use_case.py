from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.domain.structures.id import Id


class CreateHorseUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self.repository = repository

    def execute(self, horse_dto: HorseDto, owner_id: str) -> HorseDto:
        horse = Horse.create(horse_dto)
        self.repository.add(horse, Id.create(owner_id))
        return horse.dto
