from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.id import Id


@structure
class FileName(Structure):
    value: str

    @classmethod
    def create(cls, value: str) -> 'FileName':
        return cls(value=value)

    @classmethod
    def create_as_random(cls) -> 'FileName':
        return cls(value=Id.create().value)

    @property
    def randomize(self) -> 'FileName':
        return FileName(value=f'{Id.create().value}-{self.value}')
