from pydantic import BaseModel
from inngest import Inngest, Context, TriggerEvent


from equiny.core.auth.domain.events import AccountCreatedEvent
from equiny.core.profiling.use_cases import CreateOwnerUseCase
from equiny.validation.shared import NameSchema, IdSchema, EmailSchema
from equiny.pubsub.inngest.jobs.job import Job
from equiny.database.sqlalchemy.repositories.profiling import SqlalchemyOwnersRepository


class PayloadSchema(BaseModel):
    owner_name: NameSchema
    account_email: EmailSchema
    account_id: IdSchema


class CreateOwnerJob(Job):
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
                lambda: CreateOwnerJob.create_owner(payload),
            )

        return _

    @staticmethod
    async def create_owner(payload: PayloadSchema) -> None:
        with Job.sqlalchemy_session() as sqlalchemy:
            repository = SqlalchemyOwnersRepository(sqlalchemy)
            use_case = CreateOwnerUseCase(repository)
            use_case.execute(
                account_id=payload.account_id,
                owner_name=payload.owner_name,
                owner_email=payload.account_email,
            )
