from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.errors import HorseNotFoundError
from equiny.core.profiling.interfaces.repositories import HorsesRepository


class GetHorseUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self.repository = repository

    def execute(self, horse_id: str) -> HorseDto:
        horse = self.repository.find_by_id(horse_id)

        if horse is None:
            raise HorseNotFoundError

        return horse.dto
