from typing import Any


class SendMatchNotificationJob:
    KEY: str = 'notification/notify_match'

    @staticmethod
    def handle(payload: dict[str, Any]) -> None:
        print('payload', payload)
