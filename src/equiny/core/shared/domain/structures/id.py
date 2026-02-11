from uuid import uuid4
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure


@structure
class Id(Structure):
    value: str

    @staticmethod
    def create(id: str | None = None) -> 'Id':
        if id is None:
            return Id(value=str(uuid4()))

        return Id(value=id)
