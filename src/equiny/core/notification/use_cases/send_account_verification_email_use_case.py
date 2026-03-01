from equiny.core.notification.interfaces.email_sender_provider import (
    EmailProvider,
)
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text


class SendAccountVerificationEmailUseCase:
    def __init__(self, email_sender_provider: EmailProvider) -> None:
        self._email_sender_provider = email_sender_provider

    def execute(self, account_email: str, email_verification_token: str) -> None:
        email = Email.create(account_email)
        token = Text.create(email_verification_token)
        self._email_sender_provider.send_account_verification_email(email, token)
