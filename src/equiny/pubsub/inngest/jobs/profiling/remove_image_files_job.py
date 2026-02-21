from pydantic import BaseModel
from inngest import Inngest, Context, TriggerEvent

from equiny.core.profiling.domain.events.image_files_removed_event import (
    ImageFilesRemovedEvent,
)
from equiny.core.shared.domain.structures.text import Text
from equiny.core.storage.structures.file_storage_folder import FileStorageFolder
from equiny.providers.storage.supabase.supabase_file_storage_provider import (
    SupabaseFileStorageProvider,
)


class PayloadSchema(BaseModel):
    image_files_keys: list[str]


class RemoveImageFilesJob:
    @staticmethod
    def handle(inngest: Inngest):
        @inngest.create_function(
            fn_id='profiling/remove.image.files.job',
            trigger=TriggerEvent(event=ImageFilesRemovedEvent.name),
        )
        async def _(context: Context) -> None:
            payload = PayloadSchema.model_validate(context.event.data)
            await context.step.run(
                'Remove image files',
                lambda: RemoveImageFilesJob.remove_files(payload),
            )

        return _

    @staticmethod
    async def remove_files(payload: PayloadSchema) -> None:
        if not payload.image_files_keys:
            return

        provider = SupabaseFileStorageProvider()
        folder = FileStorageFolder.create_as_images()
        file_keys = [Text.create(key) for key in payload.image_files_keys]

        provider.remove_many(folder, file_keys)
