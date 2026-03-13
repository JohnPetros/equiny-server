from faker import Faker

from equiny.core.profiling.domain.structures.dtos import LocationDto
from equiny.core.profiling.domain.structures.location import Location


class LocationFaker:
    _faker = Faker()

    @staticmethod
    def fake_dto(
        city: str | None = None,
        state: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> LocationDto:
        return LocationDto(
            city=city or LocationFaker._faker.city(),
            state=state or LocationFaker._faker.state_abbr(),
            latitude=latitude
            if latitude is not None
            else float(LocationFaker._faker.latitude()),
            longitude=longitude
            if longitude is not None
            else float(LocationFaker._faker.longitude()),
        )

    @staticmethod
    def fake(
        city: str | None = None,
        state: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Location:
        return Location.create(
            LocationFaker.fake_dto(
                city=city,
                state=state,
                latitude=latitude,
                longitude=longitude,
            )
        )
