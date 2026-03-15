from pydantic import BaseModel
from inngest import Inngest, Context, TriggerEvent


from equiny.core.auth.domain.events import AccountCreatedEvent
from equiny.core.profiling.use_cases import CreateOwnerUseCase
from equiny.validation.shared import NameSchema, IdSchema, EmailSchema
from equiny.database.sqlalchemy.repositories.profiling import SqlalchemyOwnersRepository
from equiny.database.sqlalchemy import Sqlalchemy
from equiny.pubsub.inngest.inngest_broker import InngestBroker


class PayloadSchema(BaseModel):
    owner_name: NameSchema
    account_email: EmailSchema
    account_id: IdSchema
    account_email_verification_token: str | None = None


class CreateOwnerJob:
    @staticmethod
    def handle(inngest: Inngest):
        @inngest.create_function(
            fn_id='profiling/create.owner.job',
            trigger=TriggerEvent(event=AccountCreatedEvent.name),
        )
        async def _(context: Context) -> None:
            payload = PayloadSchema.model_validate(context.event.data)
            await context.step.run(
                'Create owner',
                lambda: CreateOwnerJob.create_owner(payload, inngest),
            )

        return _

    @staticmethod
    async def create_owner(payload: PayloadSchema, inngest: Inngest) -> None:
        with Sqlalchemy.session() as sqlalchemy_session:
            repository = SqlalchemyOwnersRepository(sqlalchemy_session)
            broker = InngestBroker(inngest)
            use_case = CreateOwnerUseCase(repository, broker)
            use_case.execute(
                owner_name=payload.owner_name,
                owner_email=payload.account_email,
                owner_email_verification_token=payload.account_email_verification_token,
                account_id=payload.account_id,
            )
