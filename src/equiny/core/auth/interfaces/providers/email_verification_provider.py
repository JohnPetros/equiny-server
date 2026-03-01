from typing import Protocol

from equiny.core.shared.domain.structures.logical import Logical
from equiny.core.shared.domain.structures.text import Text
from equiny.core.shared.domain.structures.email import Email


class EmailVerificationProvider(Protocol):
    def generate_verification_token(self, account_email: Email) -> Text: ...

    def verify_verification_token(self, verification_token: Text) -> Logical: ...

    def decode_email_from_token(self, verification_token: Text) -> str: ...
