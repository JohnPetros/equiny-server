import httpx

from equiny.core.notification.interfaces import PushNotificationProvider
from equiny.core.shared.domain.errors import AppError
from equiny.constants import Env
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.shared.domain.structures.text import Text


class OnesignalPushNotificationProvider(PushNotificationProvider):
    _URL: str = 'https://api.onesignal.com/notifications'

    def __init__(self, file_storage_provider: FileStorageProvider) -> None:
        self._file_storage_provider = file_storage_provider

    def send_horse_match_notification(
        self, owner_id: str, match_horse_name: str, match_horse_image: str
    ) -> None:
        payload = {
            'app_id': Env.ONESIGNAL_APP_ID,
            'target_channel': 'push',
            'include_aliases': {
                'external_id': [owner_id],
            },
            'headings': {'en': 'Novo match!'},
            'contents': {
                'en': f'{match_horse_name} deu match com seu cavalo.',
            },
            'big_picture': self._file_storage_provider.get_file_url(
                Text.create(match_horse_image)
            ).value,
        }
        headers = {
            'Authorization': f'Key {Env.ONESIGNAL_API_KEY}',
            'Content-Type': 'application/json',
        }

        try:
            response = httpx.post(
                self._URL,
                json=payload,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
        except Exception as error:
            print('error', error)
            raise AppError(
                'Erro ao enviar push de match',
                f'Falha ao enviar notificacao de match para owner {owner_id}: {error!s}',
            ) from error
