from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.logical import Logical
from equiny.core.shared.domain.structures.datetime import Datetime
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.name import Name
from equiny.core.shared.domain.structures.image import Image
from equiny.core.profiling.domain.structures.location import Location


@structure
class HorseMatch(Structure):
    owner_id: Id
    owner_name: Name
    owner_avatar: Image
    owner_location: Location
    owner_horse_id: Id
    owner_horse_name: Name
    owner_horse_image: Image
    is_viewed: Logical
    created_at: Datetime

    @classmethod
    def create(cls, dto: HorseMatchDto) -> 'HorseMatch':
        return cls(
            owner_id=Id.create(dto.owner_id),
            owner_name=Name.create(dto.owner_name),
            owner_avatar=Image.create(dto.owner_avatar),
            owner_location=Location.create(dto.owner_location),
            owner_horse_id=Id.create(dto.owner_horse_id),
            owner_horse_name=Name.create(dto.owner_horse_name),
            owner_horse_image=Image.create(dto.owner_horse_image),
            is_viewed=Logical.create(dto.is_viewed),
            created_at=Datetime.create(dto.created_at),
        )

    def view(self) -> 'HorseMatch':
        return HorseMatch(
            owner_id=self.owner_id,
            owner_name=self.owner_name,
            owner_avatar=self.owner_avatar,
            owner_location=self.owner_location,
            owner_horse_id=self.owner_horse_id,
            owner_horse_name=self.owner_horse_name,
            owner_horse_image=self.owner_horse_image,
            created_at=self.created_at,
            is_viewed=Logical.create_true(),
        )

    @property
    def dto(self) -> HorseMatchDto:
        return HorseMatchDto(
            owner_id=self.owner_id.value,
            owner_name=self.owner_name.value,
            owner_avatar=self.owner_avatar.dto,
            owner_location=self.owner_location.dto,
            owner_horse_id=self.owner_horse_id.value,
            owner_horse_name=self.owner_horse_name.value,
            owner_horse_image=self.owner_horse_image.dto,
            is_viewed=self.is_viewed.value,
            created_at=self.created_at.value,
        )
