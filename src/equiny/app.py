from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from equiny.core.shared.domain.errors import (
    AppError,
    AuthError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
    ValidationError,
)
from equiny.routers.auth import AuthRouter
from equiny.routers.docs import DocsRouter
from equiny.routers.matching import MatchingRouter
from equiny.routers.profiling import ProfilingRouter
from equiny.routers.storage import StorageRouter
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

        app.add_exception_handler(AppError, FastAPIApp.handle_exception)
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
        app.include_router(MatchingRouter.register())
        app.include_router(ProfilingRouter.register())
        app.include_router(StorageRouter.register())

        return app

    @staticmethod
    def handle_exception(_: Request, exception: Exception) -> JSONResponse:
        if isinstance(exception, AppError):
            if isinstance(exception, ValidationError):
                return JSONResponse(
                    status_code=400,
                    content={'title': exception.title, 'message': exception.message},
                )
            if isinstance(exception, (UnauthorizedError, AuthError)):
                return JSONResponse(
                    status_code=401,
                    content={'title': exception.title, 'message': exception.message},
                )
            if isinstance(exception, ForbiddenError):
                return JSONResponse(
                    status_code=403,
                    content={'title': exception.title, 'message': exception.message},
                )
            if isinstance(exception, NotFoundError):
                return JSONResponse(
                    status_code=404,
                    content={'title': exception.title, 'message': exception.message},
                )
            if isinstance(exception, ConflictError):
                return JSONResponse(
                    status_code=409,
                    content={'title': exception.title, 'message': exception.message},
                )
            if isinstance(exception, RateLimitError):
                return JSONResponse(
                    status_code=429,
                    content={'title': exception.title, 'message': exception.message},
                )
        return JSONResponse(
            status_code=500,
            content={'title': 'Erro interno do servidor', 'message': str(exception)},
        )
