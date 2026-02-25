from typing import Any

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket

from equiny.core.shared.domain.errors.app_error import AppError
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.database.sqlalchemy import Sqlalchemy
from equiny.database.sqlalchemy.repositories.conversation import (
    SqlalchemyChatsRepository,
    SqlalchemyMessagesRepository,
)
from equiny.database.sqlalchemy.repositories.profiling import (
    SqlalchemyHorsesRepository,
    SqlalchemyOwnersRepository,
)
from equiny.pipes import AuthPipe, DatabasePipe, ProvidersPipe, PubSubPipe
from equiny.pubsub.redis import RedisPubSub
from equiny.pubsub.redis.brokers import RedisConversationBroker, RedisProfilingBroker
from equiny.validation.shared import IdSchema, Schema
from equiny.websocket.channels import ConversationChannel, ProfilingChannel
from equiny.websocket import ws


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

        @router.websocket('/{owner_id}')
        async def _(
            websocket: WebSocket,
            owner_id: IdSchema,
            token: dict[str, str] = Depends(AuthPipe.verify_jwt_from_query),
            cache_provider: CacheProvider = Depends(ProvidersPipe.get_cache_provider),
            sqlalchemy: Sqlalchemy = Depends(DatabasePipe.get_sqlalchemy),
            redis_pubsub: RedisPubSub = Depends(
                PubSubPipe.get_redis_pubsub_from_websocket
            ),
        ) -> None:
            await ws.connect(owner_id, websocket)
            try:
                while True:
                    data = await websocket.receive_json()
                    json = JsonSchema.model_validate(data)

                    if json.is_from_conversation_module():
                        broker = RedisConversationBroker(redis_pubsub)

                        with sqlalchemy.session() as sqlalchemy_session:
                            chats_repository = SqlalchemyChatsRepository(
                                sqlalchemy_session
                            )
                            messages_repository = SqlalchemyMessagesRepository(
                                sqlalchemy_session
                            )
                            channel = ConversationChannel(
                                broker, chats_repository, messages_repository
                            )
                            channel.handle(json.name, json.payload)
                    elif json.is_from_profiling_module():
                        broker = RedisProfilingBroker(redis_pubsub)

                        with sqlalchemy.session() as sqlalchemy_session:
                            chats_repository = SqlalchemyChatsRepository(
                                sqlalchemy_session
                            )
                            messages_repository = SqlalchemyMessagesRepository(
                                sqlalchemy_session
                            )
                            owners_repository = SqlalchemyOwnersRepository(
                                sqlalchemy_session
                            )
                            horses_repository = SqlalchemyHorsesRepository(
                                sqlalchemy_session
                            )
                            channel = ProfilingChannel(
                                broker,
                                cache_provider,
                                owners_repository,
                                horses_repository,
                            )
                            channel.handle(json.name, json.payload)
                    else:
                        raise AppError(
                            'Event not supported', f'Event {json.name} not supported'
                        )
            finally:
                ws.disconnect(owner_id, websocket)

        return router
