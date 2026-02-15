from enum import Enum

from equiny.core.shared.domain.abstracts.structure import Structure
from equiny.core.shared.domain.decorators import structure


class FileStorageFolderValue(Enum):
    IMAGES = 'images'


@structure
class FileStorageFolder(Structure):
    value: FileStorageFolderValue

    @classmethod
    def create(cls, value: FileStorageFolderValue) -> 'FileStorageFolder':
        return cls(value=value)

    @classmethod
    def create_as_images(cls) -> 'FileStorageFolder':
        return cls(value=FileStorageFolderValue.IMAGES)

    @property
    def dto(self) -> str:
        return self.value.value
