from equiny.core.shared.domain.decorators.dto import dto


@dto
class OwnerDto:
    id: str | None = None
    name: str
    email: str
    account_id: str
