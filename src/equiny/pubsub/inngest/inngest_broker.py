from typing import Any

from equiny.core.shared.domain.abstracts import Event
from inngest import Inngest, Event as InngestEvent


class InngestBroker:
    def __init__(self, inngest: Inngest) -> None:
        self._inngest = inngest

    def publish(self, event: Event[Any]) -> None:
        print('event.payload_data', event.payload_data)
        inngest_event = InngestEvent(name=event.name, data=event.payload_data)
        print('inngest_event', inngest_event)
        self._inngest.send_sync(inngest_event)
