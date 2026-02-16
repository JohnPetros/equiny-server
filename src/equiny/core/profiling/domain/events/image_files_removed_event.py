from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    image_files_keys: list[str]


class ImageFilesRemovedEvent(Event):
    name: str = 'profiling/image.files.removed'

    def __init__(self, image_files_keys: list[str]) -> None:
        payload = Payload(
            image_files_keys=image_files_keys,
        )
        super().__init__(ImageFilesRemovedEvent.name, payload)
