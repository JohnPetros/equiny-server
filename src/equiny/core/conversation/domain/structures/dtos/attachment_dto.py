from equiny.core.shared.domain.decorators.dto import dto


@dto
class AttachmentDto:
    key: str
    name: str
    kind: str
    size: float
