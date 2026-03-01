from typing import Any

from equiny.core.shared.domain.abstracts import Event
from inngest import Inngest, Event as InngestEvent


class InngestBroker:
    def __init__(self, inngest: Inngest) -> None:
        self._inngest = inngest

    def publish(self, event: Event[Any]) -> None:
        inngest_event = InngestEvent(name=event.name, data=event.payload_data)
        self._inngest.send_sync(inngest_event)
