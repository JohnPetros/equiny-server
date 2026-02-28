from typing import Any
from equiny.core.profiling.domain.events import (
    OwnerEnteredEvent,
    OwnerExitedEvent,
    OwnerPresenceRegisteredEvent,
    OwnerPresenceUnregisteredEvent,
)
from equiny.core.profiling.interfaces.repositories import (
    HorsesRepository,
    OwnersRepository,
)
from equiny.core.profiling.use_cases import (
    RegisterOwnerPresenceUseCase,
    UnregisterOwnerPresenceUseCase,
)
from equiny.core.shared.domain.errors.app_error import AppError
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from equiny.core.shared.interfaces.broker import Broker
from equiny.validation.shared import IdSchema
from equiny.validation.shared.schema import Schema


class ProfilingChannel:
    def __init__(
        self,
        broker: Broker,
        cache_provider: CacheProvider,
        owners_repository: OwnersRepository,
        horses_repository: HorsesRepository,
    ) -> None:
        self._broker = broker
        self._cache_provider = cache_provider
        self._owners_repository = owners_repository
        self._horses_repository = horses_repository

    def handle(self, event_name: str, event_payload: Any) -> None:
        match event_name:
            case OwnerEnteredEvent.NAME:
                self._on_owner_entered(event_payload)
            case OwnerExitedEvent.NAME:
                self._on_owner_exited(event_payload)
            case _:
                raise AppError('WebSocket Error', f'Event {event_name} not supported')

    def _on_owner_entered(self, event_payload: Any) -> None:
        class PayloadSchema(Schema):
            owner_id: IdSchema

        payload = PayloadSchema.model_validate(event_payload)
        owner_id = payload.owner_id

        use_case = RegisterOwnerPresenceUseCase(
            self._cache_provider,
            self._owners_repository,
        )
        use_case.execute(owner_id)

        owner_matches = self._horses_repository.find_horse_matches_by_owner_id(
            Id.create(owner_id)
        )
        match_owner_ids = [match.owner_id.value for match in owner_matches]
        self._broker.publish(OwnerPresenceRegisteredEvent(owner_id, match_owner_ids))

    def _on_owner_exited(self, event_payload: Any) -> None:
        class PayloadSchema(Schema):
            owner_id: IdSchema

        payload = PayloadSchema.model_validate(event_payload)
        owner_id = payload.owner_id

        use_case = UnregisterOwnerPresenceUseCase(
            self._cache_provider,
            self._owners_repository,
        )
        use_case.execute(owner_id)

        owner_matches = self._horses_repository.find_horse_matches_by_owner_id(
            Id.create(owner_id)
        )
        match_owner_ids = [match.owner_id.value for match in owner_matches]
        self._broker.publish(OwnerPresenceUnregisteredEvent(owner_id, match_owner_ids))
