from equiny.core.shared.domain.decorators.dto import dto


@dto
class AttachmentDto:
    kind: str
    name: str
