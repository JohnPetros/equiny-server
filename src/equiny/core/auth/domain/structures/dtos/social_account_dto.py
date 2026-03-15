from equiny.core.shared.domain.decorators import dto


@dto
class SocialAccountDto:
    email: str
    provider: str
