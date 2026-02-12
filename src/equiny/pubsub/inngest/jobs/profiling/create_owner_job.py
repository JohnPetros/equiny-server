from inngest import Inngest, Context, TriggerEvent
from pydantic import BaseModel

from equiny.core.auth.domain.events import AccountCreatedEvent
from equiny.core.profiling.use_cases import CreateOwnerUseCase
from equiny.database.sqlalchemy.sqlalchemy import Sqlalchemy
from equiny.database.sqlalchemy.repositories.profiling import SqlalchemyOwnersRepository
from equiny.validation.shared import NameSchema, IdSchema, EmailSchema


class PayloadSchema(BaseModel):
    owner_name: NameSchema
    owner_email: EmailSchema
    account_id: IdSchema


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
                lambda: CreateOwnerJob.create_owner(payload),
            )

        return _

    @staticmethod
    async def create_owner(payload: PayloadSchema) -> None:
        repository = SqlalchemyOwnersRepository(Sqlalchemy.get_session())
        use_case = CreateOwnerUseCase(repository)
        use_case.execute(
            account_id=payload.account_id,
            owner_name=payload.owner_name,
            owner_email=payload.owner_email,
        )
