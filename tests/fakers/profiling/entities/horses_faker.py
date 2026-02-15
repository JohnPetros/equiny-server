from faker import Faker

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.structures.dtos import LocationDto
from tests.fakers.profiling.structures.location_faker import LocationFaker
from tests.fakers.profiling.structures.sex_faker import SexFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class HorsesFaker:
    _faker = Faker()

    @staticmethod
    def fake() -> Horse:
        return Horse.create(HorsesFaker.fake_dto())

    @staticmethod
    def fake_dto(
        name: str | None = None,
        birth_month: int | None = None,
        birth_year: int | None = None,
        breed: str | None = None,
        sex: str | None = None,
        location: LocationDto | None = None,
    ) -> HorseDto:
        horse_breeds = [
            'Arabian',
            'Thoroughbred',
            'Quarter Horse',
            'Appaloosa',
            'Andalusian',
            'Morgan',
            'Mustang',
            'Paint Horse',
            'Friesian',
            'Clydesdale',
        ]

        return HorseDto(
            id=IdFaker.fake().value,
            name=name or HorsesFaker._faker.first_name(),
            birth_month=birth_month or HorsesFaker._faker.random_int(min=1, max=12),
            birth_year=birth_year or HorsesFaker._faker.random_int(min=2000, max=2024),
            breed=breed or HorsesFaker._faker.random_element(elements=horse_breeds),
            location=location or LocationFaker.fake_dto(),
            sex=sex or SexFaker.fake_dto(),
        )

    @staticmethod
    def fake_many(count: int) -> list[HorseDto]:
        return [HorsesFaker.fake_dto() for _ in range(count)]
