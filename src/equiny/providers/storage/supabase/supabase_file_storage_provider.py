import uuid

from supabase import create_client

from equiny.core.shared.domain.errors import AppError
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.structures.file import File
from equiny.constants import ENV


class SupabaseFileStorageProvider:
    _BUCKET = ENV.SUPABASE_STORAGE_BUCKET

    def __init__(self) -> None:
        self.client = create_client(ENV.SUPABASE_URL, ENV.SUPABASE_KEY)

    def upload(self, file: File) -> Text:
        key = f'{file.folder.dto}/{uuid.uuid4()}-{file.name.value}'

        try:
            response = self.client.storage.from_(self._BUCKET).upload(
                key, file.data, {'content-type': file.content_type}
            )
        except Exception as error:
            raise AppError(
                'Erro no upload',
                f'Falha ao enviar arquivo "{file.name.value}" para o storage: {error!s}',
            ) from error

        return Text.create(response.full_path)

    def upload_many(self, files: list[File]) -> list[Text]:
        return [self.upload(file) for file in files]
