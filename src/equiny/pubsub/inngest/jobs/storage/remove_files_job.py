from pydantic import BaseModel
from inngest import Inngest, Context, TriggerEvent

from equiny.core.profiling.domain.events.image_files_removed_event import (
    ImagesFilesRemovedEvent,
)
from equiny.core.shared.domain.structures.text import Text
from equiny.providers.storage.supabase.supabase_file_storage_provider import (
    SupabaseFileStorageProvider,
)


class PayloadSchema(BaseModel):
    files_paths: list[str]


class RemoveFilesJob:
    @staticmethod
    def handle(inngest: Inngest):
        @inngest.create_function(
            fn_id='storage/remove.files.job',
            trigger=TriggerEvent(event=ImagesFilesRemovedEvent.name),
        )
        async def _(context: Context) -> None:
            payload = PayloadSchema.model_validate(context.event.data)
            await context.step.run(
                'Remove image files',
                lambda: RemoveFilesJob.remove_files(payload),
            )

        return _

    @staticmethod
    async def remove_files(payload: PayloadSchema) -> None:
        if not payload.files_paths:
            return

        provider = SupabaseFileStorageProvider()
        provider.remove_files(
            [Text.create(file_path) for file_path in payload.files_paths]
        )
