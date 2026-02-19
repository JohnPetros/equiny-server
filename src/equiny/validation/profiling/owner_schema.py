from pydantic import BaseModel

from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.validation.profiling.gallery_schema import ImageSchema
from equiny.validation.shared import EmailSchema, NameSchema


class OwnerSchema(BaseModel):
    name: NameSchema
    email: EmailSchema
    bio: str | None = None
    phone: str | None = None
    avatar: ImageSchema | None = None

    def to_dto(self, owner: Owner) -> OwnerDto:
        owner_dto = owner.dto
        avatar = owner_dto.avatar
        if self.avatar is not None:
            avatar = ImageDto(key=self.avatar.key, name=self.avatar.name)
        return OwnerDto(
            id=owner_dto.id,
            name=self.name,
            email=owner_dto.email,
            account_id=owner_dto.account_id,
            bio=self.bio,
            phone=self.phone,
            avatar=avatar,
            has_completed_onboarding=owner_dto.has_completed_onboarding,
        )
