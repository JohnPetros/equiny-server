from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from equiny.routers.auth import AuthRouter
from equiny.routers.docs import DocsRouter
from equiny.routers.profiling import ProfilingRouter
from equiny.rest.middlewares import (
    HandleSqlalchemySessionMiddleware,
    HandleInngestClientMiddleware,
)
from equiny.pubsub.inngest.inngest_pubsub import InngestPubSub


class FastAPIApp:
    @staticmethod
    def register() -> FastAPI:
        app = FastAPI(
            docs_url=None,
            redoc_url=None,
        )

        app.add_middleware(
            CORSMiddleware,
            allow_credentials=True,
            allow_origins=['*'],
            allow_methods=['*'],
            allow_headers=['*'],
        )
        inngest = InngestPubSub.register(app)

        HandleSqlalchemySessionMiddleware.handle(app)
        HandleInngestClientMiddleware.handle(app, inngest)

        app.include_router(AuthRouter.register())
        app.include_router(DocsRouter.register())
        app.include_router(ProfilingRouter.register())

        return app
