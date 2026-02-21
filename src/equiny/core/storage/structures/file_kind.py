from enum import Enum

from equiny.core.shared.domain.abstracts.structure import Structure
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.errors import ValidationError


class FileKindValue(Enum):
    IMAGES = 'images'


@structure
class FileKind(Structure):
    value: FileKindValue

    @classmethod
    def create(cls, value: str) -> 'FileKind':
        match value:
            case 'images':
                return cls(value=FileKindValue.IMAGES)
            case _:
                raise ValidationError(f'Pasta de storage invalida: {value}')

    @classmethod
    def create_as_images(cls) -> 'FileKind':
        return cls(value=FileKindValue.IMAGES)

    @property
    def dto(self) -> str:
        return self.value.value
