from equiny.core.profiling.domain.entities.dtos.horse_dto import HorseDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.domain.structures.id import Id


class GetOwnerHorsesUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self._repository = repository

    def execute(self, owner_id: str) -> list[HorseDto]:
        horses = self._repository.find_many_by_owner(Id.create(owner_id))
        return [horse.dto for horse in horses]
