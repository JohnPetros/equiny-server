from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.domain.entities import Owner
from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.shared.interfaces.broker import Broker
from equiny.core.profiling.domain.events.owner_created_event import OwnerCreatedEvent


class CreateOwnerUseCase:
    def __init__(self, repository: OwnersRepository, broker: Broker) -> None:
        self._repository = repository
        self._broker = broker

    def execute(
        self,
        owner_name: str,
        owner_email: str,
        owner_email_verification_token: str,
        account_id: str,
    ) -> OwnerDto:
        owner = Owner.create(
            OwnerDto(
                name=owner_name,
                email=owner_email,
                account_id=account_id,
                bio=None,
                phone=None,
                has_completed_onboarding=False,
            )
        )
        self._repository.add(owner)
        self._broker.publish(
            OwnerCreatedEvent(
                owner_id=owner.id.value,
                owner_email=owner.email.value,
                owner_email_verification_token=owner_email_verification_token,
            )
        )
        return owner.dto
