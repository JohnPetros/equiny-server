from equiny.core.shared.domain.decorators.dto import dto


@dto
class AttachmentDto:
    chat_id: str
    message_id: str
    attachment_id: str
    file_kind: str
    file_name: str
