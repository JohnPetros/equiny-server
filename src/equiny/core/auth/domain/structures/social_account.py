from equiny.core.auth.domain.structures.dtos.social_account_dto import SocialAccountDto
from equiny.core.auth.domain.structures.social_account_provider import (
    SocialAccountProvider,
)
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.email import Email


@structure
class SocialAccount(Structure):
    email: Email
    provider: SocialAccountProvider

    @classmethod
    def create(cls, email: str, provider: str) -> 'SocialAccount':
        return cls(
            email=Email.create(email),
            provider=SocialAccountProvider.create(provider),
        )

    @property
    def dto(self) -> SocialAccountDto:
        return SocialAccountDto(
            email=self.email.value,
            provider=self.provider.dto,
        )
