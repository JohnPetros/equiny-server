from equiny.core.shared.domain.decorators.dto import dto


@dto
class UploadUrlDto:
    url: str
    token: str
    file_path: str
