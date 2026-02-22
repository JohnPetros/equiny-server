from fastapi import APIRouter, Depends, WebSocket
from starlette.websockets import WebSocketDisconnect

from equiny.core.profiling.domain.structures.dtos.owner_presence_dto import (
    OwnerPresenceDto,
)
from equiny.core.profiling.use_cases import (
    RegisterOwnerPresenceUseCase,
    UnregisterOwnerPresenceUseCase,
)
from equiny.core.shared.domain.errors.app_error import AppError
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.database.sqlalchemy.repositories.profiling import SqlalchemyOwnersRepository
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.providers_pipe import ProvidersPipe
from equiny.database.sqlalchemy import Sqlalchemy
from equiny.websocket.rooms.ws import Ws
from equiny.validation.shared import IdSchema


class OwnersPresenceRoom:
    @staticmethod
    def handle(router: APIRouter) -> None:
        ws = Ws()

        @router.websocket('/{owner_id}/presence')
        async def _(
            socket: WebSocket,
            owner_id: IdSchema,
            _: dict[str, str] = Depends(AuthPipe.verify_jwt_from_query),
            sqlalchemy: Sqlalchemy = Depends(DatabasePipe.get_sqlalchemy),
            cache_provider: CacheProvider = Depends(ProvidersPipe.get_cache_provider),
        ) -> None:
            channel_key = 'owners:presence'
            await ws.connect(channel_key, socket)
            is_registered = False

            try:
                with sqlalchemy.session() as sqlalchemy_session:
                    repository = SqlalchemyOwnersRepository(sqlalchemy_session)
                    register_use_case = RegisterOwnerPresenceUseCase(
                        cache_provider=cache_provider,
                        repository=repository,
                    )
                    register_use_case.execute(owner_id)
                    is_registered = True

                await ws.broadcast(
                    channel_key,
                    OwnerPresenceDto(owner_id=owner_id, is_online=True),
                )

                while True:
                    await socket.receive_text()
            except (WebSocketDisconnect, RuntimeError):
                pass
            except AppError:
                await socket.close()
            finally:
                if is_registered:
                    with sqlalchemy.session() as sqlalchemy_session:
                        repository = SqlalchemyOwnersRepository(sqlalchemy_session)
                        unregister_use_case = UnregisterOwnerPresenceUseCase(
                            cache_provider=cache_provider,
                            repository=repository,
                        )
                        unregister_use_case.execute(owner_id)

                    await ws.broadcast(
                        channel_key,
                        OwnerPresenceDto(owner_id=owner_id, is_online=False),
                    )

                ws.disconnect(channel_key, socket)
