from equiny.core.shared.domain.decorators.entity import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.shared.domain.structures.logical import Logical
from equiny.core.shared.domain.structures.name import Name
from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text
from equiny.core.shared.domain.structures.phone import Phone


@entity
class Owner(Entity):
    name: Name
    email: Email
    account_id: Id
    bio: Text | None
    phone: Phone | None
    has_completed_onboarding: Logical

    @classmethod
    def create(cls, dto: OwnerDto) -> 'Owner':
        return cls(
            id=Id.create(dto.id),
            name=Name.create(dto.name),
            email=Email.create(dto.email),
            account_id=Id.create(dto.account_id),
            bio=Text.create(dto.bio) if dto.bio is not None else None,
            phone=Phone.create(dto.phone) if dto.phone is not None else None,
            has_completed_onboarding=Logical.create(value=dto.has_completed_onboarding),
        )

    @property
    def dto(self) -> OwnerDto:
        return OwnerDto(
            id=self.id.value,
            name=self.name.value,
            email=self.email.value,
            account_id=self.account_id.value,
            bio=self.bio.value if self.bio is not None else None,
            phone=self.phone.value if self.phone is not None else None,
            has_completed_onboarding=self.has_completed_onboarding.value,
        )
