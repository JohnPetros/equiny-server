from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.structures.dtos import FileDto
from equiny.core.storage.structures.file_kind import FileKind


@structure
class File(Structure):
    name: Text
    kind: FileKind
    data: bytes
    content_type: str

    @classmethod
    def create(cls, dto: FileDto) -> 'File':
        return cls(
            name=Text.create(dto.name),
            kind=FileKind.create(dto.kind),
            data=dto.data,
            content_type=dto.content_type,
        )

    @property
    def dto(self) -> FileDto:
        return FileDto(
            name=self.name.value,
            kind=self.kind.dto,
            data=self.data,
            content_type=self.content_type,
        )
