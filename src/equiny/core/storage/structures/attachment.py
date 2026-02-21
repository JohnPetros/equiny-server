from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.storage.structures.file_kind import FileKind
from equiny.core.shared.domain.structures.text import Text


@structure
class Attachment(Structure):
    chat_id: Id
    message_id: Id
    attachment_id: Id
    kind: FileKind
    name: Text
