import resend

from equiny.constants import Env
from equiny.core.notification.interfaces.email_sender_provider import EmailProvider
from equiny.core.shared.domain.errors import AppError
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text
from equiny.providers.email.constants.email_verification_html import (
    EMAIL_VERIFICATION_HTML,
)


class ResendEmailProvider(EmailProvider):
    def send_account_verification_email(
        self, account_email: Email, verification_token: Text
    ) -> None:
        verification_url = f'{Env.EQUINY_SERVER_URL}/auth/verify-email?token={verification_token.value}'

        html = EMAIL_VERIFICATION_HTML.format(verification_url=verification_url)

        try:
            resend.api_key = Env.RESEND_API_KEY

            params: resend.Emails.SendParams = {
                'from': Env.RESEND_SENDER_EMAIL,
                'to': ['nosoca6230@pazuric.com'],
                'subject': 'Reenvio de confirmacao de email - Equiny',
                'html': html,
            }

            resend.Emails.send(params)

        except Exception as error:
            raise AppError(
                'Erro ao enviar email',
                f'Falha ao reenviar email de verificacao para {account_email.value}: {error!s}',
            ) from error
