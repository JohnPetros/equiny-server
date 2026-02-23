from typing import Any

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket

from equiny.core.shared.domain.errors.app_error import AppError
from equiny.database.sqlalchemy import Sqlalchemy
from equiny.database.sqlalchemy.repositories.conversation import (
    SqlalchemyChatsRepository,
    SqlalchemyMessagesRepository,
)
from equiny.database.sqlalchemy.repositories.profiling import SqlalchemyOwnersRepository
from equiny.pipes import AuthPipe, DatabasePipe
from equiny.providers.cache.redis.redis_cache_provider import RedisCacheProvider
from equiny.validation.shared import IdSchema, Schema
from equiny.websocket.conversation.conversation_channel import ConversationChannel
from equiny.websocket.profiling.profiling_channel import ProfilingChannel
from equiny.websocket.ws import Ws


class JsonSchema(Schema):
    payload: Any
    name: str

    def is_from_profiling_module(self) -> bool:
        return self.name.startswith('profiling/')

    def is_from_conversation_module(self) -> bool:
        return self.name.startswith('conversation/')


class WebSocketRouter:
    @staticmethod
    def register() -> APIRouter:
        router = APIRouter(prefix='/websocket', tags=['Websocket'])
        ws = Ws()

        @router.websocket('/{owner_id}')
        async def _(
            websocket: WebSocket,
            owner_id: IdSchema,
            token: dict[str, str] = Depends(AuthPipe.verify_jwt_from_query),
            sqlalchemy: Sqlalchemy = Depends(DatabasePipe.get_sqlalchemy),
        ) -> None:
            await ws.connect(owner_id, websocket)
            while True:
                data = await websocket.receive_json()
                json = JsonSchema.model_validate(data)
                if json.is_from_conversation_module():
                    with sqlalchemy.session() as sqlalchemy_session:
                        chats_repository = SqlalchemyChatsRepository(sqlalchemy_session)
                        messages_repository = SqlalchemyMessagesRepository(
                            sqlalchemy_session
                        )
                        channel = ConversationChannel(
                            ws, chats_repository, messages_repository
                        )
                        channel.handle(json.name, json.payload)
                elif json.is_from_profiling_module():
                    with sqlalchemy.session() as sqlalchemy_session:
                        chats_repository = SqlalchemyChatsRepository(sqlalchemy_session)
                        messages_repository = SqlalchemyMessagesRepository(
                            sqlalchemy_session
                        )
                        owners_repository = SqlalchemyOwnersRepository(
                            sqlalchemy_session
                        )
                        cache_provider = RedisCacheProvider()
                        channel = ProfilingChannel(
                            ws, cache_provider, owners_repository
                        )
                        channel.handle(json.name, json.payload)
                else:
                    raise AppError(
                        'Event not supported', f'Event {json.name} not supported'
                    )

        return router
