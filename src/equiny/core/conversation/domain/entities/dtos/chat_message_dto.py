from datetime import datetime
from equiny.core.shared.domain.decorators.dto import dto

from equiny.core.conversation.domain.structures.dtos.attachment_dto import AttachmentDto


@dto
class MessageDto:
    id: str | None = None
    sender_id: str
    content: str | None = None
    attachments: list[AttachmentDto]
    sent_at: datetime | None = None
    updated_at: datetime | None = None
    is_viewed_by_recipient: bool | None = None
