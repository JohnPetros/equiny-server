from typing import ClassVar, TypedDict

from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.interfaces.repositories.horsers_repository import (
    HorsesRepository,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.domain.entities import Horse, Owner
from equiny.fakers.profiling.entities import HorsesFaker, OwnersFaker

from equiny.core.profiling.domain.structures.image import Image
from equiny.core.profiling.domain.structures.location import LocationDto
from equiny.fakers.profiling.structures import ImageFaker


class HorseWithImages(TypedDict):
    horse: Horse
    images: list[Image]


class ProfilingSeeder:
    _HORSES: ClassVar[list[HorseWithImages]] = [
        {
            'horse': HorsesFaker.fake(
                name='Fandangueiro',
                birth_month=9,
                birth_year=2016,
                height=1.46,
                breed='criolo',
                sex='male',
                location=LocationDto(state='RS', city='Bagé'),
            ),
            'images': [
                ImageFaker.fake(
                    key='fandagueiro-5076b08d-3d86-440d-b5eb-335ea79bc418.png'
                ),
                ImageFaker.fake(
                    key='fandagueiro-897ee6a0-6865-4b47-aa78-c8704cbad9ee.png'
                ),
                ImageFaker.fake(
                    key='fandagueiro-7e690ea4-1f81-4992-a8b4-469ed42eb080.png'
                ),
                ImageFaker.fake(
                    key='fandagueiro-30379524-7c48-4443-86a2-925f19f06fc5.png'
                ),
            ],
        },
        {
            'horse': HorsesFaker.fake(
                name='Gaivota',
                birth_month=4,
                birth_year=2019,
                height=1.55,
                breed='mangalarga marchador',
                sex='female',
                location=LocationDto(state='MG', city='Uberaba'),
            ),
            'images': [
                ImageFaker.fake(key='gaivota-a6ac04e1-6215-4c40-bd78-2a5ff7b81a71.png'),
                ImageFaker.fake(key='gaivota-c5de04b6-ebaf-4a66-836d-f128b3cff373.png'),
                ImageFaker.fake(key='gaivota-4feb5333-ed73-4043-9163-f364cb5b1e3a.png'),
            ],
        },
        {
            'horse': HorsesFaker.fake(
                name='Tordilho',
                birth_month=1,
                birth_year=2018,
                height=1.50,
                breed='quarto de milha',
                sex='male',
                location=LocationDto(state='SP', city='Ribeirão Preto'),
            ),
            'images': [],
        },
        {
            'horse': HorsesFaker.fake(
                name='Sereia',
                birth_month=6,
                birth_year=2020,
                height=1.62,
                breed='campolina',
                sex='female',
                location=LocationDto(state='BA', city='Feira de Santana'),
            ),
            'images': [],
        },
        {
            'horse': HorsesFaker.fake(
                name='Valente',
                birth_month=10,
                birth_year=2017,
                height=1.70,
                breed='puro sangue inglês',
                sex='male',
                location=LocationDto(state='RJ', city='Teresópolis'),
            ),
            'images': [],
        },
    ]

    def __init__(
        self, horses_repository: HorsesRepository, owners_repository: OwnersRepository
    ) -> None:
        self._horses_repository = horses_repository
        self._owners_repository = owners_repository

    def seed(self, accounts_ids: list[Id]) -> None:
        owners = self._seed_owners(accounts_ids)
        self._seed_horsers(owners)

    def _seed_owners(self, accounts_ids: list[Id]) -> list[Owner]:
        owners: list[Owner] = []
        for account_id in accounts_ids:
            owners.append(
                OwnersFaker.fake(
                    account_id=account_id.value,
                    has_completed_onboarding=True,
                )
            )
        self._owners_repository.add_many(owners)
        return owners

    def _seed_horsers(self, owners: list[Owner]) -> None:
        for index, horse_data in enumerate(self._HORSES):
            self._horses_repository.add(horse_data['horse'], owners[index].id)
            self._horses_repository.add_many_images(
                horse_data['horse'].id, horse_data['images']
            )
