from equiny.core.profiling.domain.entities import Owner
from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.profiling.domain.errors.owner_not_found_error import OwnerNotFoundError
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.shared.domain.structures.id import Id


class UpdateOwnerUseCase:
    def __init__(self, repository: OwnersRepository) -> None:
        self._repository: OwnersRepository = repository

    def execute(self, owner_dto: OwnerDto) -> OwnerDto:
        self._find_owner(Id.create(owner_dto.id))
        owner = Owner.create(owner_dto)
        self._repository.replace(owner)
        return owner.dto

    def _find_owner(self, owner_id: Id) -> Owner:
        owner = self._repository.find_by_id(owner_id)
        if owner is None:
            raise OwnerNotFoundError
        return owner
