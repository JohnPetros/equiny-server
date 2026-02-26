from equiny.core.profiling.domain.structures.dtos import OwnerPresenceDto
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.logical import Logical
from equiny.core.shared.domain.structures.datetime import Datetime


@structure
class OwnerPresence(Structure):
    owner_id: Id
    is_online: Logical
    last_seen_at: Datetime | None = None

    @classmethod
    def create(cls, dto: OwnerPresenceDto) -> 'OwnerPresence':
        return cls(
            owner_id=Id.create(dto.owner_id),
            is_online=Logical.create(dto.is_online),
            last_seen_at=Datetime.create(dto.last_seen_at)
            if dto.last_seen_at is not None
            else None,
        )

    @property
    def dto(self) -> OwnerPresenceDto:
        return OwnerPresenceDto(
            owner_id=self.owner_id.value,
            is_online=self.is_online.value,
            last_seen_at=self.last_seen_at.value
            if self.last_seen_at is not None
            else None,
        )
