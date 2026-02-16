from typing import Protocol

from equiny.core.storage.structures.file import File
from equiny.core.shared.domain.structures.text import Text


class FileStorageProvider(Protocol):
    def upload(self, file: File) -> Text: ...

    def upload_many(self, files: list[File]) -> list[Text]: ...
