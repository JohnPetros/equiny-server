from pydantic.dataclasses import dataclass
from equiny.core.shared.domain.abstracts import Event


@dataclass
class _Payload:
    image_files_keys: list[str]
    files_paths: list[str]


class ImagesFilesRemovedEvent(Event[_Payload]):
    name: str = 'profiling/images.files.removed'

    def __init__(self, files_paths: list[str]) -> None:
        payload = _Payload(
            image_files_keys=files_paths,
            files_paths=files_paths,
        )
        super().__init__(ImagesFilesRemovedEvent.name, payload)
