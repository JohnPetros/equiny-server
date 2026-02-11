from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from equiny.routers.auth import AuthRouter
from equiny.routers.docs import DocsRouter
from equiny.routers.profiling import ProfilingRouter
from equiny.middlewares.database.handle_sqlalchemy_session_middleware import (
    HandleSqlalchemySessionMiddleware,
)


def create_app() -> FastAPI:
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
    HandleSqlalchemySessionMiddleware.handle(app)

    app.include_router(AuthRouter.register())
    app.include_router(DocsRouter.register())
    app.include_router(ProfilingRouter.register())

    return app
