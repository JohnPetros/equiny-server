from uuid import uuid4, UUID

from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.errors import ValidationError


@structure
class Id(Structure):
    value: str

    @staticmethod
    def create(id: str | None = None) -> 'Id':
        if id is None:
            return Id(value=str(uuid4()))

        if not UUID(id).version == 4:
            raise ValidationError(f'Invalid UUIDv4: {id}')

        return Id(value=id)
