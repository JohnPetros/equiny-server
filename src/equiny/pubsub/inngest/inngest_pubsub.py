from logging import getLogger

from inngest import Inngest, fast_api
from fastapi import FastAPI

from equiny.constants import ENV
from equiny.pubsub.inngest.jobs.profiling import CreateOwnerJob


class InngestPubSub:
    @staticmethod
    def register(app: FastAPI) -> Inngest:
        inngest = Inngest(
            app_id='Equiny PubSub',
            logger=getLogger('uvicorn'),
            signing_key=ENV.INNGEST_SIGNING_KEY,
        )

        fast_api.serve(
            app,
            inngest,
            functions=[
                CreateOwnerJob.handle(inngest),
            ],
        )

        return inngest

    @staticmethod
    def register_profiling_jobs(inngest: Inngest):
        return [
            CreateOwnerJob.handle(inngest),
        ]
