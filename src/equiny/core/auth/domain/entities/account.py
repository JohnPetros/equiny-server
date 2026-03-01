from equiny.core.shared.domain.decorators.entity import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.email import Email
from equiny.core.shared.domain.structures.text import Text
from equiny.core.shared.domain.structures.logical import Logical


@entity
class Account(Entity):
    email: Email
    password: Text
    is_verified: Logical

    @classmethod
    def create(cls, dto: AccountDto) -> 'Account':
        return cls(
            id=Id.create(dto.id),
            email=Email.create(dto.email),
            password=Text.create(dto.password),
            is_verified=Logical.create(dto.is_verified),
        )

    @property
    def dto(self) -> AccountDto:
        return AccountDto(
            id=self.id.value,
            email=self.email.value,
            password=self.password.value,
            is_verified=self.is_verified.value,
        )
