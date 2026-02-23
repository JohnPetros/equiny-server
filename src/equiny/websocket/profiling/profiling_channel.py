from typing import Any
from equiny.constants import ROOMS_KEYS
from equiny.core.profiling.domain.events import OwnerEnteredEvent, OwnerLeftEvent
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.use_cases import (
    RegisterOwnerPresenceUseCase,
    UnregisterOwnerPresenceUseCase,
)
from equiny.core.shared.domain.errors.app_error import AppError
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.validation.shared import IdSchema
from equiny.validation.shared.schema import Schema
from equiny.websocket.profiling.profiling_broker import ProfilingBroker
from equiny.websocket.ws import Ws


class ProfilingChannel:
    def __init__(
        self,
        ws: Ws,
        cache_provider: CacheProvider,
        repository: OwnersRepository,
    ) -> None:
        self._ws = ws
        self._cache_provider = cache_provider
        self._repository = repository
        self._broker = ProfilingBroker(ws)

    def handle(self, event_name: str, event_payload: Any) -> None:
        match event_name:
            case OwnerEnteredEvent.name:
                self._on_owner_entered(event_payload)
            case OwnerLeftEvent.name:
                self._on_owner_left(event_payload)
            case _:
                raise AppError('WebSocket Error', f'Event {event_name} not supported')

    def _on_owner_entered(self, event_payload: Any) -> None:
        class PayloadSchema(Schema):
            owner_id: IdSchema

        payload = PayloadSchema.model_validate(event_payload)
        owner_id = payload.owner_id

        self._ws.enter_room(
            f'{ROOMS_KEYS.INBOX}:{owner_id}',
            owner_id,
        )
        use_case = RegisterOwnerPresenceUseCase(
            self._cache_provider,
            self._repository,
            self._broker,
        )
        use_case.execute(owner_id)

    def _on_owner_left(self, event_payload: Any) -> None:
        class PayloadSchema(Schema):
            owner_id: IdSchema

        payload = PayloadSchema.model_validate(event_payload)
        owner_id = payload.owner_id

        self._ws.leave_room(
            f'{ROOMS_KEYS.INBOX}:{owner_id}',
            owner_id,
        )
        use_case = UnregisterOwnerPresenceUseCase(
            self._cache_provider,
            self._repository,
            self._broker,
        )
        use_case.execute(owner_id)
