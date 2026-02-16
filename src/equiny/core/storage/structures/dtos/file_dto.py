from equiny.core.shared.domain.decorators.dto import dto


@dto
class FileDto:
    name: str
    folder: str
    data: bytes
    content_type: str
