from logging import getLogger

from inngest import Inngest, fast_api
from fastapi import FastAPI

from equiny.constants import Env
from equiny.pubsub.inngest.jobs.profiling import (
    CreateOwnerJob,
    NotifyHorseMatchJob,
)
from equiny.pubsub.inngest.jobs.storage import RemoveFilesJob


class InngestPubSub:
    @staticmethod
    def register(app: FastAPI) -> Inngest:
        inngest = Inngest(
            app_id='Equiny PubSub',
            logger=getLogger('uvicorn'),
            signing_key=Env.INNGEST_SIGNING_KEY,
        )

        fast_api.serve(
            app,
            inngest,
            functions=[
                *InngestPubSub.register_profiling_jobs(inngest, app),
                *InngestPubSub.register_storage_jobs(inngest),
            ],
        )

        return inngest

    @staticmethod
    def register_profiling_jobs(inngest: Inngest, app: FastAPI):
        return [
            CreateOwnerJob.handle(inngest),
            NotifyHorseMatchJob.handle(inngest, app),
        ]

    @staticmethod
    def register_storage_jobs(inngest: Inngest):
        return [
            RemoveFilesJob.handle(inngest),
        ]
