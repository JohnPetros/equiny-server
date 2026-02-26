from equiny.core.shared.domain.decorators.entity import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.shared.domain.structures.datetime import Datetime
from equiny.core.shared.domain.structures.logical import Logical
from equiny.core.shared.domain.structures.name import Name
from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text
from equiny.core.shared.domain.structures.phone import Phone
from equiny.core.shared.domain.structures.image import Image


@entity
class Owner(Entity):
    name: Name
    email: Email
    account_id: Id
    bio: Text | None
    phone: Phone | None
    avatar: Image | None
    has_completed_onboarding: Logical
    last_presence_at: Datetime | None

    @classmethod
    def create(cls, dto: OwnerDto) -> 'Owner':
        return cls(
            id=Id.create(dto.id),
            name=Name.create(dto.name),
            email=Email.create(dto.email),
            account_id=Id.create(dto.account_id),
            bio=Text.create(dto.bio) if dto.bio is not None else None,
            phone=Phone.create(dto.phone) if dto.phone is not None else None,
            avatar=Image.create(dto.avatar) if dto.avatar is not None else None,
            has_completed_onboarding=Logical.create(value=dto.has_completed_onboarding),
            last_presence_at=Datetime.create(dto.last_presence_at)
            if dto.last_presence_at is not None
            else None,
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
            avatar=self.avatar.dto if self.avatar is not None else None,
            has_completed_onboarding=self.has_completed_onboarding.value,
            last_presence_at=(
                self.last_presence_at.value
                if self.last_presence_at is not None
                else None
            ),
        )

    def exit_presence(self) -> None:
        self.last_presence_at = Datetime.create_at_now()

    def set_account_id(self, account_id: Id) -> None:
        self.account_id = account_id
