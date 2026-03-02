from equiny.core.shared.domain.decorators.dto import dto


@dto
class AccountDto:
    id: str | None = None
    email: str
    password: str
    is_verified: bool = False
