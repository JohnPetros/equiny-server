from pathlib import Path

from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures import FileStorageFolder


_IMAGES_PATH = Path(__file__).resolve().parents[5] / 'tests' / 'files' / 'images'
_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
_CONTENT_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
}


class StorageSeeder:
    def __init__(self, file_storage_provider: FileStorageProvider) -> None:
        self._file_storage_provider = file_storage_provider

    def seed(self) -> None:
        self._file_storage_provider.remove_all(FileStorageFolder.create_as_images())
        items = self._collect_image_items()
        if items:
            self._file_storage_provider.upload_many_with_keys(
                FileStorageFolder.create_as_images(), items
            )

    def _collect_image_items(self) -> list[tuple[Text, bytes, str]]:
        items: list[tuple[Text, bytes, str]] = []
        if not _IMAGES_PATH.exists():
            return items
        for path in _IMAGES_PATH.rglob('*'):
            if path.is_file() and path.suffix.lower() in _IMAGE_EXTENSIONS:
                key = path.name
                data = path.read_bytes()
                content_type = _CONTENT_TYPES.get(
                    path.suffix.lower(), 'application/octet-stream'
                )
                items.append((Text.create(key), data, content_type))
        return items
