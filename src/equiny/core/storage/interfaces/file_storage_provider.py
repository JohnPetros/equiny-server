from typing import Protocol

from equiny.core.storage.structures import UploadUrl
from equiny.core.storage.structures.file import File
from equiny.core.shared.domain.structures.text import Text


class FileStorageProvider(Protocol):
    def upload(self, file: File, upload_url: UploadUrl) -> Text: ...

    def generate_upload_url(self, file_path: Text) -> UploadUrl: ...

    def generate_upload_urls(self, files_paths: list[Text]) -> list[UploadUrl]: ...

    def remove_files(self, file_paths: list[Text]) -> None: ...

    def remove_all_files(self) -> None: ...
