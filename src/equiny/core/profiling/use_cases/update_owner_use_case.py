from equiny.core.profiling.domain.entities import Owner
from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.profiling.domain.errors.owner_not_found_error import OwnerNotFoundError
from equiny.core.profiling.domain.events.image_files_removed_event import (
    ImagesFilesRemovedEvent,
)
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.interfaces.broker import Broker
from equiny.core.shared.domain.structures.image import Image


class UpdateOwnerUseCase:
    def __init__(self, repository: OwnersRepository, broker: Broker) -> None:
        self._repository: OwnersRepository = repository
        self._broker: Broker = broker

    def execute(self, owner_id: str, owner_dto: OwnerDto) -> OwnerDto:
        current_owner = self._find_owner(Id.create(owner_id))
        owner = Owner.create(owner_dto)
        owner.id = current_owner.id
        if owner.avatar is None and current_owner.avatar is not None:
            self._publish_image_files_removed_event(current_owner.avatar)

        if (
            owner.avatar is not None
            and current_owner.avatar is not None
            and owner.avatar.key.value != current_owner.avatar.key.value
        ):
            self._publish_image_files_removed_event(current_owner.avatar)

        self._repository.replace(owner)
        return owner.dto

    def _find_owner(self, owner_id: Id) -> Owner:
        owner = self._repository.find_by_id(owner_id)
        if owner is None:
            raise OwnerNotFoundError
        return owner

    def _publish_image_files_removed_event(self, avatar: Image) -> None:
        event = ImagesFilesRemovedEvent(files_paths=[avatar.key.value])
        self._broker.publish(event)
