from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.decimal import Decimal
from equiny.core.shared.domain.structures.text import Text
from equiny.core.conversation.domain.structures.attachment_kind import AttachmentKind
from equiny.core.conversation.domain.structures.dtos.attachment_dto import AttachmentDto


@structure
class Attachment(Structure):
    key: Text
    name: Text
    kind: AttachmentKind
    size: Decimal

    @classmethod
    def create(cls, dto: AttachmentDto) -> 'Attachment':
        return cls(
            key=Text.create(dto.key),
            name=Text.create(dto.name),
            kind=AttachmentKind.create(dto.kind),
            size=Decimal.create(dto.size),
        )

    @property
    def dto(self) -> AttachmentDto:
        return AttachmentDto(
            key=self.key.value,
            name=self.name.value,
            size=self.size.value,
            kind=self.kind.dto,
        )
