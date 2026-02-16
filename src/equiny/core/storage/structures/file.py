from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.structures.dtos import FileDto
from equiny.core.storage.structures.file_storage_folder import FileStorageFolder


@structure
class File(Structure):
    name: Text
    folder: FileStorageFolder
    data: bytes
    content_type: str

    @classmethod
    def create(cls, dto: FileDto) -> 'File':
        return cls(
            name=Text.create(dto.name),
            folder=FileStorageFolder.create(dto.folder),
            data=dto.data,
            content_type=dto.content_type,
        )

    @property
    def dto(self) -> FileDto:
        return FileDto(
            name=self.name.value,
            folder=self.folder.dto,
            data=self.data,
            content_type=self.content_type,
        )
