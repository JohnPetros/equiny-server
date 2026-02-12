from equiny.core.shared.domain.decorators.entity import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.shared.domain.structures.name import Name
from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.email import Email


@entity
class Owner(Entity):
    name: Name
    email: Email
    account_id: Id

    @classmethod
    def create(cls, dto: OwnerDto) -> 'Owner':
        return cls(
            id=Id.create(dto.id),
            name=Name.create(dto.name),
            email=Email.create(dto.email),
            account_id=Id.create(dto.account_id),
        )

    @property
    def dto(self) -> OwnerDto:
        return OwnerDto(
            id=self.id.value,
            name=self.name.value,
            email=self.email.value,
            account_id=self.account_id.value,
        )
