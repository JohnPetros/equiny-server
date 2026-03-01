from typing import Protocol

from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text


class EmailProvider(Protocol):
    def send_account_verification_email(
        self, account_email: Email, verification_token: Text
    ) -> None: ...
