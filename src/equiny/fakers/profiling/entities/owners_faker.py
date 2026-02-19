from faker import Faker

from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.fakers.shared.structures.id_faker import IdFaker


class OwnersFaker:
    _faker = Faker()

    @staticmethod
    def fake(
        name: str | None = None,
        email: str | None = None,
        account_id: str | None = None,
        bio: str | None = None,
        phone: str | None = None,
        avatar: ImageDto | None = None,
        has_completed_onboarding: bool = False,
    ) -> Owner:
        return Owner.create(
            OwnersFaker.fake_dto(
                has_completed_onboarding=has_completed_onboarding,
                name=name,
                email=email,
                account_id=account_id,
                bio=bio,
                phone=phone,
                avatar=avatar,
            )
        )

    @staticmethod
    def fake_dto(
        name: str | None = None,
        email: str | None = None,
        account_id: str | None = None,
        bio: str | None = None,
        phone: str | None = None,
        avatar: ImageDto | None = None,
        has_completed_onboarding: bool = False,
    ) -> OwnerDto:
        return OwnerDto(
            id=IdFaker.fake().value,
            name=name or OwnersFaker._faker.name(),
            email=email or OwnersFaker._faker.email(),
            account_id=account_id or IdFaker.fake().value,
            bio=bio,
            phone=phone,
            avatar=avatar,
            has_completed_onboarding=has_completed_onboarding,
        )
