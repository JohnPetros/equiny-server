from equiny.core.profiling.domain.entities.dtos.owner_dto import OwnerDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.shared.domain.structures.dtos.image_dto import ImageDto
from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel


class OwnersMapper:
    @staticmethod
    def to_entity(owner_model: OwnerModel) -> Owner:
        return Owner.create(OwnersMapper.to_dto(owner_model))

    @staticmethod
    def to_dto(owner_model: OwnerModel) -> OwnerDto:
        avatar = None
        if owner_model.avatar_key is not None:
            avatar = ImageDto(
                key=owner_model.avatar_key,
                name=owner_model.avatar_name or '',
            )
        return OwnerDto(
            id=owner_model.id,
            name=owner_model.name,
            email=owner_model.email,
            account_id=owner_model.account_id,
            bio=owner_model.bio,
            phone=owner_model.phone,
            avatar=avatar,
            has_completed_onboarding=owner_model.has_completed_onboarding,
        )

    @staticmethod
    def to_model(owner: Owner) -> OwnerModel:
        avatar_key = None
        avatar_name = None
        if owner.avatar is not None:
            avatar_key = owner.avatar.key.value
            avatar_name = owner.avatar.name.value
        return OwnerModel(
            id=owner.id.value,
            name=owner.name.value,
            email=owner.email.value,
            account_id=owner.account_id.value,
            avatar_key=avatar_key,
            avatar_name=avatar_name,
            bio=owner.bio.value if owner.bio is not None else None,
            phone=owner.phone.value if owner.phone is not None else None,
            has_completed_onboarding=owner.has_completed_onboarding.value,
        )
