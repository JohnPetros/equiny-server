from enum import Enum

from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure


class AttachmentKindValue(Enum):
    IMAGE = 'image'
    AUDIO = 'audio'
    DOCUMENT = 'document'


@structure
class AttachmentKind(Structure):
    value: AttachmentKindValue

    @classmethod
    def create(cls, value: str) -> 'AttachmentKind':
        return cls(value=AttachmentKindValue(value))

    @property
    def dto(self) -> str:
        return self.value.value
