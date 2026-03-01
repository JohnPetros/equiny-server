from typing import Protocol


class PushNotificationProvider(Protocol):
    def send_horse_match_notification(
        self, owner_id: str, match_horse_name: str, match_horse_image: str
    ) -> None: ...
