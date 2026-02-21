from equiny.core.conversation.domain.structures.attachment import Attachment
from equiny.core.conversation.domain.structures.dtos.attachment_dto import AttachmentDto
from equiny.core.shared.domain.structures.id import Id
from equiny.database.sqlalchemy.models.conversation.attachment_model import (
    AttachmentModel,
)


class AttachmentsMapper:
    @staticmethod
    def to_entity(model: AttachmentModel) -> Attachment:
        dto = AttachmentDto(
            key=model.key,
            name=model.name,
            kind=model.kind,
            size=model.size,
        )
        return Attachment.create(dto)

    @staticmethod
    def to_model(attachment: Attachment, message_id: str) -> AttachmentModel:
        dto = attachment.dto
        return AttachmentModel(
            id=Id.create().value,
            message_id=message_id,
            key=dto.key,
            name=dto.name,
            kind=dto.kind,
            size=dto.size,
        )
