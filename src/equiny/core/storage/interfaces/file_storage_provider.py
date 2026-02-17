from typing import Protocol

from equiny.core.storage.structures.file import File
from equiny.core.storage.structures.file_storage_folder import FileStorageFolder
from equiny.core.shared.domain.structures.text import Text


class FileStorageProvider(Protocol):
    def upload(self, file: File) -> Text: ...

    def upload_many(self, files: list[File]) -> list[Text]: ...

    def upload_many_with_keys(
        self,
        folder: FileStorageFolder,
        items: list[tuple[Text, bytes, str]],
    ) -> list[Text]: ...

    def remove_many(self, folder: FileStorageFolder, file_keys: list[Text]) -> None: ...

    def remove_all(self, folder: FileStorageFolder) -> None: ...
