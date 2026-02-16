from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.domain.entities import Owner
from equiny.core.profiling.domain.entities.dtos import OwnerDto


class CreateOwnerUseCase:
    def __init__(self, repository: OwnersRepository) -> None:
        self.repository = repository

    def execute(self, owner_name: str, owner_email: str, account_id: str) -> OwnerDto:
        owner = Owner.create(
            OwnerDto(
                name=owner_name,
                email=owner_email,
                account_id=account_id,
                has_completed_onboarding=False,
            )
        )
        self.repository.add(owner)
        return owner.dto
