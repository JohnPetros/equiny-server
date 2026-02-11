from equiny.core.shared.domain.decorators.entity import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.shared.domain.structures.id import Id


@entity
class Account(Entity):
    email: str
    password: str

    @staticmethod
    def create(dto: AccountDto) -> 'Account':
        return Account(id=Id.create(dto.id), email=dto.email, password=dto.password)
