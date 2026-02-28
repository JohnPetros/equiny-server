from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from inngest import Inngest, Context, TriggerEvent


from equiny.core.matching.domain.events import MatchCreatedEvent
from equiny.core.profiling.use_cases.notify_horse_match_use_case import (
    NotifyHorseMatchUseCase,
)
from equiny.pubsub.redis.brokers.redis_profiling_broker import RedisProfilingBroker
from equiny.validation.shared import IdSchema
from equiny.database.sqlalchemy.repositories.profiling import (
    SqlalchemyHorsesRepository,
)
from equiny.database.sqlalchemy import Sqlalchemy


class _PayloadSchema(BaseModel):
    horse_a_id: IdSchema
    horse_b_id: IdSchema
    created_at: datetime


class NotifyHorseMatchJob:
    @staticmethod
    def handle(inngest: Inngest, app: FastAPI):
        @inngest.create_function(
            fn_id='profiling/notify.horse.match.job',
            trigger=TriggerEvent(event=MatchCreatedEvent.NAME),
        )
        async def _(context: Context) -> None:
            payload = _PayloadSchema.model_validate(context.event.data)
            await context.step.run(
                'Notify horse match',
                lambda: NotifyHorseMatchJob.notify_horse_match(app, payload),
            )

        return _

    @staticmethod
    async def notify_horse_match(app: FastAPI, payload: _PayloadSchema) -> None:
        with Sqlalchemy.session() as sqlalchemy:
            horses_repository = SqlalchemyHorsesRepository(sqlalchemy)
            broker = RedisProfilingBroker(app.state.redis_pubsub)
            use_case = NotifyHorseMatchUseCase(horses_repository, broker)
            use_case.execute(
                horse_a_id=payload.horse_a_id,
                horse_b_id=payload.horse_b_id,
            )
