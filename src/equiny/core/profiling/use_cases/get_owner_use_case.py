from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.domain.entities.dtos.owner_dto import OwnerDto
from equiny.core.profiling.domain.errors import OwnerNotFoundError


class GetOwnerUseCase:
    def __init__(self, repository: OwnersRepository) -> None:
        self._repository = repository

    def execute(self, owner_id: str) -> OwnerDto:
        owner = self._repository.find_by_id(Id.create(owner_id))
        if owner is None:
            raise OwnerNotFoundError
        return owner.dto
