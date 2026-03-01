from equiny.core.notification.interfaces import PushNotificationProvider


class SendHorseMatchPushNotificationUseCase:
    def __init__(self, provider: PushNotificationProvider) -> None:
        self._provider = provider

    def execute(
        self, owner_id: str, match_horse_name: str, match_horse_image: str
    ) -> None:
        self._provider.send_horse_match_notification(
            owner_id=owner_id,
            match_horse_name=match_horse_name,
            match_horse_image=match_horse_image,
        )
