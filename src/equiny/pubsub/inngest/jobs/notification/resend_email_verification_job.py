from pydantic import BaseModel
from inngest import Context, Inngest, TriggerEvent

from equiny.core.auth.domain.events.email_verification_requested_event import (
    EmailVerificationRequestedEvent,
)
from equiny.core.notification.use_cases.send_account_verification_email_use_case import (
    SendAccountVerificationEmailUseCase,
)
from equiny.providers.email.resend import ResendEmailProvider
from equiny.validation.shared import EmailSchema


class PayloadSchema(BaseModel):
    account_email: EmailSchema
    email_verification_token: str


class ResendEmailVerificationJob:
    @staticmethod
    def handle(inngest: Inngest):
        @inngest.create_function(
            fn_id='notification/resend.email.verification.job',
            trigger=TriggerEvent(event=EmailVerificationRequestedEvent.name),
        )
        async def _(context: Context) -> None:
            payload = PayloadSchema.model_validate(context.event.data)
            await context.step.run(
                'Resend verification email',
                lambda: ResendEmailVerificationJob.resend_verification_email(payload),
            )

        return _

    @staticmethod
    async def resend_verification_email(payload: PayloadSchema) -> None:
        email_sender_provider = ResendEmailProvider()
        use_case = SendAccountVerificationEmailUseCase(email_sender_provider)
        use_case.execute(
            account_email=payload.account_email,
            email_verification_token=payload.email_verification_token,
        )
