from faker import Faker

from equiny.core.profiling.domain.structures.sex import Sex, SexValue


class SexFaker:
    _faker = Faker()

    @staticmethod
    def fake_dto() -> str:
        return SexFaker._faker.random_element(
            elements=[SexValue.MALE.value, SexValue.FEMALE.value]
        )

    @staticmethod
    def fake() -> Sex:
        sex_value = SexFaker.fake_dto()
        if sex_value == SexValue.MALE.value:
            return Sex.create_as_male()

        return Sex.create_as_female()
