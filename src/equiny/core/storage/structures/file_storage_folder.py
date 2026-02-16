from enum import Enum

from equiny.core.shared.domain.abstracts.structure import Structure
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.errors import ValidationError


class FileStorageFolderValue(Enum):
    IMAGES = 'images'


@structure
class FileStorageFolder(Structure):
    value: FileStorageFolderValue

    @classmethod
    def create(cls, value: str) -> 'FileStorageFolder':
        try:
            return cls(value=FileStorageFolderValue(value))
        except ValueError as error:
            raise ValidationError(f'Pasta de storage invalida: {value}') from error

    @classmethod
    def create_as_images(cls) -> 'FileStorageFolder':
        return cls(value=FileStorageFolderValue.IMAGES)

    @property
    def dto(self) -> str:
        return self.value.value
