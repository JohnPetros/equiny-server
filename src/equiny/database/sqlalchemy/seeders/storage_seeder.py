from pathlib import Path

from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures import FileKind
from equiny.core.storage.structures.dtos import FileDto
from equiny.core.storage.structures.file import File


_PROFILING_FILES_PATH = (
    Path(__file__).resolve().parents[5] / 'tests' / 'files' / 'profiling'
)
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
        self._file_storage_provider.remove_all_files()
        items = self._collect_image_items()
        if items:
            file_paths = [file_path for file_path, _, _, _ in items]
            upload_urls = self._file_storage_provider.generate_upload_urls(file_paths)

            for (_, key, data, content_type), upload_url in zip(
                items, upload_urls, strict=True
            ):
                file = File.create(
                    FileDto(
                        name=key.value,
                        kind=FileKind.create_as_images().dto,
                        data=data,
                        content_type=content_type,
                    )
                )
                self._file_storage_provider.upload(
                    file=file,
                    upload_url=upload_url,
                )

    def _collect_image_items(self) -> list[tuple[Text, Text, bytes, str]]:
        items: list[tuple[Text, Text, bytes, str]] = []
        if not _PROFILING_FILES_PATH.exists():
            return items
        for path in _PROFILING_FILES_PATH.rglob('*'):
            if path.is_file() and path.suffix.lower() in _IMAGE_EXTENSIONS:
                relative_path_parts = path.relative_to(_PROFILING_FILES_PATH).parts
                if len(relative_path_parts) < 3:
                    continue

                owner_or_horse = relative_path_parts[0]
                entity_id = relative_path_parts[1]
                file_name = path.name
                data = path.read_bytes()
                content_type = _CONTENT_TYPES.get(
                    path.suffix.lower(), 'application/octet-stream'
                )

                if owner_or_horse == 'owners':
                    file_path = Text.create(
                        f'/profiling/owners/{entity_id}/avatar/{file_name}'
                    )
                elif owner_or_horse == 'horses':
                    file_path = Text.create(
                        f'/profiling/horses/{entity_id}/gallery/{file_name}'
                    )
                else:
                    continue

                items.append((file_path, Text.create(file_name), data, content_type))
        return items
