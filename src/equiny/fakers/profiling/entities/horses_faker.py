from faker import Faker

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.structures.dtos import LocationDto
from equiny.fakers.profiling.structures.location_faker import LocationFaker
from equiny.fakers.profiling.structures.sex_faker import SexFaker
from equiny.fakers.shared.structures.id_faker import IdFaker


class HorsesFaker:
    _faker = Faker()

    @staticmethod
    def fake(
        name: str | None = None,
        birth_month: int | None = None,
        birth_year: int | None = None,
        height: float | None = None,
        breed: str | None = None,
        sex: str | None = None,
        location: LocationDto | None = None,
        is_active: bool | None = None,
    ) -> Horse:
        return Horse.create(
            HorsesFaker.fake_dto(
                name, birth_month, birth_year, height, breed, sex, location, is_active
            )
        )

    @staticmethod
    def fake_dto(
        name: str | None = None,
        birth_month: int | None = None,
        birth_year: int | None = None,
        height: float | None = None,
        breed: str | None = None,
        sex: str | None = None,
        location: LocationDto | None = None,
        is_active: bool | None = None,
    ) -> HorseDto:
        horse_breeds = [
            'quarto de milha',
            'mangalarga marchador',
            'criolo',
            'puro sangue inglês',
            'arabe',
            'campolina',
            'outra',
        ]

        return HorseDto(
            id=IdFaker.fake().value,
            name=name or HorsesFaker._faker.first_name(),
            birth_month=birth_month or HorsesFaker._faker.random_int(min=1, max=12),
            birth_year=birth_year or HorsesFaker._faker.random_int(min=2000, max=2024),
            height=height
            or HorsesFaker._faker.pyfloat(min_value=0, max_value=3, right_digits=2),
            breed=breed or HorsesFaker._faker.random_element(elements=horse_breeds),
            location=location or LocationFaker.fake_dto(),
            sex=sex or SexFaker.fake_dto(),
            is_active=True if is_active is None else is_active,
        )

    @staticmethod
    def fake_many(count: int) -> list[Horse]:
        return [HorsesFaker.fake() for _ in range(count)]

    @staticmethod
    def fake_many_dto(count: int) -> list[HorseDto]:
        return [HorsesFaker.fake_dto() for _ in range(count)]
