from pydantic import BaseModel

from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.validation.shared import EmailSchema, NameSchema


class OwnerSchema(BaseModel):
    name: NameSchema
    email: EmailSchema
    bio: str | None = None
    phone: str | None = None

    def to_dto(self, owner: Owner) -> OwnerDto:
        owner_dto = owner.dto
        return OwnerDto(
            id=owner_dto.id,
            name=self.name,
            email=owner_dto.email,
            account_id=owner_dto.account_id,
            bio=self.bio,
            phone=self.phone,
            has_completed_onboarding=owner_dto.has_completed_onboarding,
        )
