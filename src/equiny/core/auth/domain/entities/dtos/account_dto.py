from dataclasses import field

from equiny.core.auth.domain.structures.dtos.social_account_dto import SocialAccountDto
from equiny.core.shared.domain.decorators.dto import dto


def _default_social_accounts() -> list[SocialAccountDto]:
    return []


@dto
class AccountDto:
    id: str | None = None
    email: str
    password: str | None
    is_verified: bool = False
    social_accounts: list[SocialAccountDto] = field(
        default_factory=_default_social_accounts
    )
