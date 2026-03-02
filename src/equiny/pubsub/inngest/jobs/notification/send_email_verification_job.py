from pydantic import BaseModel
from inngest import Context, Inngest, TriggerEvent

from equiny.core.profiling.domain.events.owner_created_event import OwnerCreatedEvent
from equiny.core.notification.use_cases.send_account_verification_email_use_case import (
    SendAccountVerificationEmailUseCase,
)
from equiny.providers.email.resend import ResendEmailProvider
from equiny.validation.shared import EmailSchema


class _PayloadSchema(BaseModel):
    owner_email: EmailSchema
    owner_email_verification_token: str


class SendEmailVerificationJob:
    @staticmethod
    def handle(inngest: Inngest):
        @inngest.create_function(
            fn_id='notification/send.email.verification.job',
            trigger=TriggerEvent(event=OwnerCreatedEvent.NAME),
        )
        async def _(context: Context) -> None:
            payload = _PayloadSchema.model_validate(context.event.data)
            print('notification/send.email.verification.job', payload)
            await context.step.run(
                'Send verification email',
                lambda: SendEmailVerificationJob.send_verification_email(payload),
            )

        return _

    @staticmethod
    async def send_verification_email(payload: _PayloadSchema) -> None:
        email_sender_provider = ResendEmailProvider()
        use_case = SendAccountVerificationEmailUseCase(email_sender_provider)
        use_case.execute(
            account_email=payload.owner_email,
            email_verification_token=payload.owner_email_verification_token,
        )
