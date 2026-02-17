import uuid

from supabase import create_client
from equiny.core.shared.domain.errors import AppError
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures.file import File
from equiny.core.storage.structures.file_storage_folder import FileStorageFolder
from equiny.constants import ENV


class SupabaseFileStorageProvider(FileStorageProvider):
    _BUCKET = ENV.SUPABASE_STORAGE_BUCKET

    def __init__(self) -> None:
        self.supabase = create_client(ENV.SUPABASE_URL, ENV.SUPABASE_KEY)

    def upload(self, file: File) -> Text:
        key = f'{uuid.uuid4()}-{file.name.value}'
        path = f'{file.folder.dto}/{key}'

        try:
            self.supabase.storage.from_(self._BUCKET).upload(
                path, file.data, {'content-type': file.content_type}
            )
        except Exception as error:
            raise AppError(
                'Erro no upload',
                f'Falha ao enviar arquivo "{file.name.value}" para o storage: {error!s}',
            ) from error

        return Text.create(key)

    def upload_many(self, files: list[File]) -> list[Text]:
        return [self.upload(file) for file in files]

    def upload_many_with_keys(
        self,
        folder: FileStorageFolder,
        items: list[tuple[Text, bytes, str]],
    ) -> list[Text]:
        keys: list[Text] = []
        for key, data, content_type in items:
            path = f'{folder.dto}/{key.value}'
            try:
                self.supabase.storage.from_(self._BUCKET).upload(
                    path, data, {'content-type': content_type}
                )
                keys.append(key)
            except Exception as error:
                raise AppError(
                    'Erro no upload',
                    f'Falha ao enviar arquivo "{key.value}" para o storage: {error!s}',
                ) from error
        return keys

    def remove_many(self, folder: FileStorageFolder, file_keys: list[Text]) -> None:
        if not file_keys:
            return

        paths = [f'{folder.dto}/{key.value}' for key in file_keys]

        try:
            self.supabase.storage.from_(self._BUCKET).remove(paths)
        except Exception as error:
            raise AppError(
                'Erro na remoção',
                f'Falha ao remover arquivos do storage: {error!s}',
            ) from error

    def remove_all(self, folder: FileStorageFolder) -> None:
        all_paths = self.supabase.storage.from_('equiny').list(
            path='images', options={'search': ''}
        )
        if not all_paths:
            return
        paths = [f'{folder.dto}/{path["name"]}' for path in all_paths]
        self.supabase.storage.from_(self._BUCKET).remove(paths)
