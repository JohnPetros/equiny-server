from storage3._sync.file_api import SyncBucketProxy
from supabase import Client, create_client

from equiny.core.shared.domain.errors import AppError
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.interfaces.file_storage_provider import FileStorageProvider
from equiny.core.storage.structures import UploadUrl
from equiny.core.storage.structures.dtos import UploadUrlDto
from equiny.core.storage.structures.file import File
from equiny.constants import ENV


class SupabaseFileStorageProvider(FileStorageProvider):
    _BUCKET = ENV.SUPABASE_STORAGE_BUCKET
    _supabase: Client

    def __init__(self) -> None:
        self._supabase = create_client(ENV.SUPABASE_URL, ENV.SUPABASE_KEY)

    def generate_upload_url(self, file_path: Text) -> UploadUrl:
        try:
            signed_upload_url = self._supabase.storage.from_(
                self._BUCKET
            ).create_signed_upload_url(file_path.value)
        except Exception as error:
            raise AppError(
                'Erro ao gerar URL de upload',
                f'Falha ao gerar URL de upload para o caminho "{file_path.value}": {error!s}',
            ) from error

        return UploadUrl.create(
            UploadUrlDto(
                url=signed_upload_url['signed_url'],
                token=signed_upload_url['token'],
                file_path=file_path.value,
            )
        )

    def generate_upload_urls(self, files_paths: list[Text]) -> list[UploadUrl]:
        upload_urls: list[UploadUrl] = []
        for file_path in files_paths:
            upload_urls.append(self.generate_upload_url(file_path=file_path))
        return upload_urls

    def upload(self, file: File, upload_url: UploadUrl) -> Text:
        path = self._normalize_file_path(upload_url.file_path.value)

        try:
            self._supabase.storage.from_(self._BUCKET).upload_to_signed_url(
                path=path,
                token=upload_url.token.value,
                file=file.data,
            )
        except Exception as error:
            raise AppError(
                'Erro no upload',
                f'Falha ao enviar arquivo "{file.name.value}" para o storage: {error!s}',
            ) from error

        file_name = path.split('/')[-1]
        return Text.create(file_name)

    def remove_files(self, file_paths: list[Text]) -> None:
        if not file_paths:
            return

        paths = [self._normalize_file_path(file_path.value) for file_path in file_paths]

        try:
            self._supabase.storage.from_(self._BUCKET).remove(paths)
        except Exception as error:
            raise AppError(
                'Erro na remoção',
                f'Falha ao remover arquivos do storage: {error!s}',
            ) from error

    def remove_all_files(self) -> None:
        try:
            storage = self._supabase.storage.from_(self._BUCKET)

            all_file_paths = self._list_all_file_paths(storage, path='')

            if not all_file_paths:
                return

            # remove em lotes para evitar payload grande
            batch_size = 100
            for i in range(0, len(all_file_paths), batch_size):
                batch = all_file_paths[i : i + batch_size]
                storage.remove(batch)

        except Exception as error:
            raise AppError(
                'Erro na remoção',
                f'Falha ao remover todos os arquivos: {error!s}',
            ) from error

    def _list_all_file_paths(
        self, storage: SyncBucketProxy, path: str = ''
    ) -> list[str]:
        results: list[str] = []
        offset = 0
        limit = 100

        while True:
            items = storage.list(
                path=path,
                options={
                    'limit': limit,
                    'offset': offset,
                    'sortBy': {'column': 'name', 'order': 'asc'},
                },
            )

            if not items:
                break

            for item in items:
                name = item.get('name')
                if not name:
                    continue

                full_path = f'{path}/{name}' if path else name

                is_folder = item.get('id') is None

                if is_folder:
                    results.extend(self._list_all_file_paths(storage, path=full_path))
                else:
                    results.append(full_path)

            # paginação
            if len(items) < limit:
                break
            offset += limit

        return results

    def _normalize_file_path(self, file_path: str) -> str:
        return file_path.lstrip('/')
