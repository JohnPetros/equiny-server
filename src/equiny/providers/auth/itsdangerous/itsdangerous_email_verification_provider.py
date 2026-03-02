from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from equiny.constants import Env
from equiny.core.auth.interfaces.providers.email_verification_provider import (
    EmailVerificationProvider,
)
from equiny.core.shared.domain.errors import AppError
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text
from equiny.core.shared.domain.structures.logical import Logical


class ItsdangerousEmailVerificationProvider(EmailVerificationProvider):
    _TTL_SECONDS: int = 86400  # 24h

    def generate_verification_token(self, account_email: Email) -> Text:
        serializer = URLSafeTimedSerializer(Env.EMAIL_VERIFICATION_SECRET)
        token = serializer.dumps(account_email.value)
        return Text.create(token)

    def verify_verification_token(self, verification_token: Text) -> Logical:
        serializer = URLSafeTimedSerializer(Env.EMAIL_VERIFICATION_SECRET)
        try:
            serializer.loads(verification_token.value, max_age=self._TTL_SECONDS)
            return Logical.create_true()
        except (SignatureExpired, BadSignature):
            return Logical.create_false()

    def decode_email_from_token(self, verification_token: Text) -> str:
        serializer = URLSafeTimedSerializer(Env.EMAIL_VERIFICATION_SECRET)
        try:
            email: str = serializer.loads(
                verification_token.value, max_age=self._TTL_SECONDS
            )
        except (SignatureExpired, BadSignature) as error:
            raise AppError(
                'Token inválido', 'Não foi possível decodificar o email do token'
            ) from error
        else:
            return email
