from equiny.core.shared.domain.decorators.dto import dto


@dto
class JwtDto:
    access_token: str
