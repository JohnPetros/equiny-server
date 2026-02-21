from dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class Payload:
    files_paths: list[str]


class ImagesFilesRemovedEvent(Event):
    name: str = 'profiling/images.files.removed'

    def __init__(self, files_paths: list[str]) -> None:
        payload = Payload(
            files_paths=files_paths,
        )
        super().__init__(ImagesFilesRemovedEvent.name, payload)
