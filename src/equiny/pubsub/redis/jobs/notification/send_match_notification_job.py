from typing import Any
from pydantic import BaseModel

from equiny.core.notification.use_cases import SendHorseMatchPushNotificationUseCase
from equiny.providers.notification import OnesignalPushNotificationProvider
from equiny.providers.storage.supabase.supabase_file_storage_provider import (
    SupabaseFileStorageProvider,
)
from equiny.validation.shared import IdSchema


class _HorseImagePayloadSchema(BaseModel):
    key: str


class _HorseMatchPayloadSchema(BaseModel):
    owner_horse_name: str
    owner_horse_image: _HorseImagePayloadSchema


class _PayloadSchema(BaseModel):
    owner_id: IdSchema
    horse_match: _HorseMatchPayloadSchema


class SendMatchNotificationJob:
    KEY: str = 'notification/notify_match'

    @staticmethod
    def handle(payload: dict[str, Any]) -> None:
        validated_payload = _PayloadSchema.model_validate(payload)
        file_storage_provider = SupabaseFileStorageProvider()
        provider = OnesignalPushNotificationProvider(file_storage_provider)
        use_case = SendHorseMatchPushNotificationUseCase(provider)
        use_case.execute(
            owner_id=validated_payload.owner_id,
            match_horse_name=validated_payload.horse_match.owner_horse_name,
            match_horse_image=validated_payload.horse_match.owner_horse_image.key,
        )
