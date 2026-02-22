from datetime import datetime

from equiny.core.shared.domain.decorators import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.text import Text
from equiny.core.shared.domain.structures.datetime import Datetime
from equiny.core.conversation.domain.entities.dtos import MessageDto
from equiny.core.conversation.domain.structures.attachment import Attachment
from equiny.core.shared.domain.structures.logical import Logical


@entity
class Message(Entity):
    content: Text | None = None
    sender_id: Id
    attachments: list[Attachment]
    sent_at: Datetime
    is_read_by_recipient: Logical
    updated_at: Datetime | None = None

    @classmethod
    def create(cls, dto: MessageDto) -> 'Message':
        return cls(
            id=Id.create(dto.id),
            sender_id=Id.create(dto.sender_id),
            content=Text.create(dto.content) if dto.content else None,
            attachments=[
                Attachment.create(attachment) for attachment in dto.attachments
            ],
            sent_at=Datetime.create(dto.sent_at or datetime.now()),
            is_read_by_recipient=Logical.create(dto.is_read_by_recipient or False),
            updated_at=Datetime.create(dto.updated_at) if dto.updated_at else None,
        )

    def become_read(self) -> None:
        self.is_read_by_recipient = Logical.create_true()

    @property
    def dto(self) -> MessageDto:
        return MessageDto(
            id=self.id.value,
            sender_id=self.sender_id.value,
            content=self.content.value if self.content else None,
            attachments=[attachment.dto for attachment in self.attachments],
            sent_at=self.sent_at.value,
            updated_at=self.updated_at.value if self.updated_at else None,
            is_read_by_recipient=self.is_read_by_recipient.value,
        )
