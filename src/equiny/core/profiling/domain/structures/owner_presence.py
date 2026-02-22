from equiny.core.profiling.domain.structures.dtos import OwnerPresenceDto
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.logical import Logical


@structure
class OwnerPresence(Structure):
    owner_id: Id
    is_online: Logical

    @classmethod
    def create(cls, dto: OwnerPresenceDto) -> 'OwnerPresence':
        return cls(
            owner_id=Id.create(dto.owner_id),
            is_online=Logical.create(dto.is_online),
        )

    @property
    def dto(self) -> OwnerPresenceDto:
        return OwnerPresenceDto(
            owner_id=self.owner_id.value,
            is_online=self.is_online.value,
        )
