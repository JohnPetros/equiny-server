from equiny.core.shared.domain.decorators.dto import dto


@dto
class SignUpResultDto:
    id: str
    email: str
    is_verified: bool = False
