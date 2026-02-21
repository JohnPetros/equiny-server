from equiny.core.shared.domain.decorators import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.name import Name
from equiny.core.shared.domain.structures.image import Image
from equiny.core.conversation.domain.entities.dtos.recipient_dto import RecipientDto


@entity
class Recipient(Entity):
    id: Id
    name: Name | None = None
    avatar: Image | None = None

    @classmethod
    def create(cls, dto: RecipientDto) -> 'Recipient':
        return cls(
            id=Id.create(dto.id),
            name=Name.create(dto.name) if dto.name else None,
            avatar=Image.create(dto.avatar) if dto.avatar else None,
        )

    @property
    def dto(self) -> RecipientDto:
        return RecipientDto(
            id=self.id.value,
            name=self.name.value if self.name else None,
            avatar=self.avatar.dto if self.avatar else None,
        )
