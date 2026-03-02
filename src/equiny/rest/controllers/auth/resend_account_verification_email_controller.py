from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.auth.interfaces.providers.email_verification_provider import (
    EmailVerificationProvider,
)
from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.use_cases.resend_account_verification_email_use_case import (
    ResendAccountVerificationEmailUseCase,
)
from equiny.core.shared.interfaces.broker import Broker
from equiny.pipes import DatabasePipe, ProvidersPipe, PubSubPipe
from equiny.validation.auth import ResendVerificationEmailSchema
from equiny.validation.shared import Schema


class ResponseSchema(Schema):
    message: str


class ResendAccountVerificationEmailController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/resend-verification-email',
            status_code=HTTPStatus.OK,
            response_model=ResponseSchema,
        )
        def _(
            body: ResendVerificationEmailSchema,
            repository: AccountsRepository = Depends(
                DatabasePipe.get_accounts_repository
            ),
            email_verification_provider: EmailVerificationProvider = Depends(
                ProvidersPipe.get_email_verification_provider
            ),
            broker: Broker = Depends(PubSubPipe.get_broker_from_request),
        ) -> ResponseSchema:
            use_case = ResendAccountVerificationEmailUseCase(
                repository=repository,
                email_verification_provider=email_verification_provider,
                broker=broker,
            )
            use_case.execute(body.account_email)
            return ResponseSchema(message='Email de verificacao reenviado')
