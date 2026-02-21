from typing import ClassVar, TypedDict

from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.interfaces.repositories.horsers_repository import (
    HorsesRepository,
)
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.domain.entities import Horse, Owner
from equiny.fakers.profiling.entities import HorsesFaker, OwnersFaker

from equiny.core.shared.domain.structures.image import Image
from equiny.core.profiling.domain.structures.location import LocationDto
from equiny.fakers.profiling.structures import ImageFaker


class HorseWithImages(TypedDict):
    horse: Horse
    images: list[Image]


class OwnerWithAvatar(TypedDict):
    owner: Owner
    avatar: Image


class ProfilingSeeder:
    _HORSES: ClassVar[list[HorseWithImages]] = [
        {
            'horse': HorsesFaker.fake(
                id='01KHPD158QDMXWTGENWZK5DFYD',
                name='Fandangueiro',
                birth_month=9,
                birth_year=2016,
                height=1.90,
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
                id='01KHPDT8C9BM21QXZPT8QF2QYT',
                name='Gaivota',
                birth_month=4,
                birth_year=2019,
                height=1.55,
                breed='mangalarga marchador',
                sex='female',
                location=LocationDto(state='RS', city='Bagé'),
            ),
            'images': [
                ImageFaker.fake(key='gaivota-a6ac04e1-6215-4c40-bd78-2a5ff7b81a71.png'),
                ImageFaker.fake(key='gaivota-c5de04b6-ebaf-4a66-836d-f128b3cff373.png'),
                ImageFaker.fake(key='gaivota-4feb5333-ed73-4043-9163-f364cb5b1e3a.png'),
            ],
        },
        {
            'horse': HorsesFaker.fake(
                id='01KHPDTD59JH4AYNP759MEXE8S',
                name='Tordilho',
                birth_month=1,
                birth_year=2018,
                height=1.50,
                breed='quarto de milha',
                sex='male',
                location=LocationDto(state='RS', city='Bagé'),
            ),
            'images': [
                ImageFaker.fake(
                    key='tordilho-5a341c27-334a-4af4-b59b-1f3ec3c616a0.png'
                ),
                ImageFaker.fake(
                    key='tordilho-a6ac04e1-6215-4c40-bd78-2a5ff7b81a71.png'
                ),
                ImageFaker.fake(
                    key='tordilho-e40074c4-20b7-4ee7-8b8d-10693f27acd7.png'
                ),
                ImageFaker.fake(
                    key='tordilho-fe195f5f-f680-456a-a905-d5ce7c3f3e8f.png'
                ),
            ],
        },
        {
            'horse': HorsesFaker.fake(
                id='01KHPDTHJDG6AE016WS4D4Q9CW',
                name='Sereia',
                birth_month=6,
                birth_year=2020,
                height=1.62,
                breed='campolina',
                sex='female',
                location=LocationDto(state='RS', city='Bagé'),
            ),
            'images': [
                ImageFaker.fake(key='sereia-201b4f9e-2612-4efd-bac2-dee8ebde4bfb.png'),
                ImageFaker.fake(key='sereia-0854b929-d77c-4f53-b890-4049087b54d8.png'),
                ImageFaker.fake(key='sereia-b38cd13b-da92-40ed-b9c0-fbc657c7a995.png'),
            ],
        },
        {
            'horse': HorsesFaker.fake(
                id='01KHPDTQ5NEQWYZ11FY9YV9P1B',
                name='Valente',
                birth_month=10,
                birth_year=2017,
                height=1.70,
                breed='puro sangue inglês',
                sex='male',
                location=LocationDto(state='RS', city='Bagé'),
            ),
            'images': [
                ImageFaker.fake(key='valente-9d800c36-ef70-4df8-8234-ab16c369ddd9.png'),
                ImageFaker.fake(key='valente-56ca1044-4873-4f6a-8e02-7c0c27f08076.png'),
                ImageFaker.fake(key='valente-a4d570a9-f683-4898-8a0a-9bb882154d43.png'),
                ImageFaker.fake(key='valente-e6762a70-cca2-4cad-b032-526e9fdbcca7.png'),
            ],
        },
        {
            'horse': HorsesFaker.fake(
                id='01KHPDV1X7YJ6N8N6ZK4J9P7A1',
                name='Brasa',
                birth_month=3,
                birth_year=2021,
                height=1.58,
                breed='mangalarga marchador',
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
                id='01KHPDV7M3H8P7S0D8Q6W2K9CZ',
                name='Aurora',
                birth_month=8,
                birth_year=2019,
                height=1.60,
                breed='campolina',
                sex='female',
                location=LocationDto(state='RS', city='Bagé'),
            ),
            'images': [
                ImageFaker.fake(
                    key='tordilho-5a341c27-334a-4af4-b59b-1f3ec3c616a0.png'
                ),
                ImageFaker.fake(
                    key='tordilho-a6ac04e1-6215-4c40-bd78-2a5ff7b81a71.png'
                ),
                ImageFaker.fake(
                    key='tordilho-e40074c4-20b7-4ee7-8b8d-10693f27acd7.png'
                ),
                ImageFaker.fake(
                    key='tordilho-fe195f5f-f680-456a-a905-d5ce7c3f3e8f.png'
                ),
            ],
        },
        {
            'horse': HorsesFaker.fake(
                id='01KHPDVC0Y3QJ8TQ6M4R2A9V6N',
                name='Jatobá',
                birth_month=12,
                birth_year=2017,
                height=1.52,
                breed='quarto de milha',
                sex='male',
                location=LocationDto(state='RS', city='Bagé'),
            ),
            'images': [
                ImageFaker.fake(key='sereia-201b4f9e-2612-4efd-bac2-dee8ebde4bfb.png'),
                ImageFaker.fake(key='sereia-0854b929-d77c-4f53-b890-4049087b54d8.png'),
                ImageFaker.fake(key='sereia-b38cd13b-da92-40ed-b9c0-fbc657c7a995.png'),
            ],
        },
        {
            'horse': HorsesFaker.fake(
                id='01KHPDVH9Q2B1X6G7M8N3P0R5S',
                name='Maré Alta',
                birth_month=5,
                birth_year=2020,
                height=1.47,
                breed='criolo',
                sex='female',
                location=LocationDto(state='RS', city='Bagé'),
            ),
            'images': [
                ImageFaker.fake(key='valente-9d800c36-ef70-4df8-8234-ab16c369ddd9.png'),
                ImageFaker.fake(key='valente-56ca1044-4873-4f6a-8e02-7c0c27f08076.png'),
                ImageFaker.fake(key='valente-a4d570a9-f683-4898-8a0a-9bb882154d43.png'),
                ImageFaker.fake(key='valente-e6762a70-cca2-4cad-b032-526e9fdbcca7.png'),
            ],
        },
        {
            'horse': HorsesFaker.fake(
                id='01KHPDVN4W6Z2Y7X8C3V9B1N0M',
                name='Rouxinol',
                birth_month=2,
                birth_year=2016,
                height=1.72,
                breed='puro sangue inglês',
                sex='male',
                location=LocationDto(state='RS', city='Bagé'),
            ),
            'images': [
                ImageFaker.fake(
                    key='tordilho-5a341c27-334a-4af4-b59b-1f3ec3c616a0.png'
                ),
                ImageFaker.fake(
                    key='tordilho-a6ac04e1-6215-4c40-bd78-2a5ff7b81a71.png'
                ),
                ImageFaker.fake(
                    key='tordilho-e40074c4-20b7-4ee7-8b8d-10693f27acd7.png'
                ),
                ImageFaker.fake(
                    key='tordilho-fe195f5f-f680-456a-a905-d5ce7c3f3e8f.png'
                ),
            ],
        },
    ]

    _OWNERS: ClassVar[list[Owner]] = [
        OwnersFaker.fake(
            name='Mariana Duarte',
            email='mariana.duarte@equiny.dev',
            bio='Criadora e apaixonada por esportes equestres. Procuro conexões para treino e eventos.',
            phone='21981234567',
            avatar=ImageFaker.fake_dto(key='mariana.duarte@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
        OwnersFaker.fake(
            name='Rafael Monteiro',
            email='rafael.monteiro@equiny.dev',
            bio='Proprietário de cavalos de marcha. Gosto de trocar experiência sobre manejo e bem-estar.',
            phone='31992345678',
            avatar=ImageFaker.fake_dto(key='rafael.monteiro@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
        OwnersFaker.fake(
            name='Camila Nascimento',
            email='camila.nascimento@equiny.dev',
            bio='Iniciante no mundo equestre. Buscando aprender e conhecer pessoas da região.',
            phone=None,
            avatar=ImageFaker.fake_dto(key='camila.nascimento@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
        OwnersFaker.fake(
            name='Bruno Almeida',
            email='bruno.almeida@equiny.dev',
            bio='Focado em performance e treinamento. Curto trilhas e provas de velocidade.',
            phone='11973456789',
            avatar=ImageFaker.fake_dto(key='bruno.almeida@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
        OwnersFaker.fake(
            name='Fernanda Ribeiro',
            email='fernanda.ribeiro@equiny.dev',
            bio='Veterinária e entusiasta de criação responsável. Aqui pra fazer networking e ajudar.',
            phone='71984567890',
            avatar=ImageFaker.fake_dto(key='fernanda.ribeiro@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
        OwnersFaker.fake(
            name='Lucas Ferreira',
            email='lucas.ferreira@equiny.dev',
            bio='Apaixonado por cavalgadas longas. Curto planejar rotas e conhecer novas pessoas.',
            phone='31987654321',
            avatar=ImageFaker.fake_dto(key='rafael.monteiro@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
        OwnersFaker.fake(
            name='Juliana Santos',
            email='juliana.santos@equiny.dev',
            bio='Começando no hipismo. Busco dicas de treino, cuidados e bons lugares pra praticar.',
            phone=None,
            avatar=ImageFaker.fake_dto(key='camila.nascimento@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
        OwnersFaker.fake(
            name='Tiago Oliveira',
            email='tiago.oliveira@equiny.dev',
            bio='Gosto de manejo e bem-estar. Sempre trocando ideia sobre nutrição e rotina do cavalo.',
            phone='11998765432',
            avatar=ImageFaker.fake_dto(key='bruno.almeida@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
        OwnersFaker.fake(
            name='Patrícia Lima',
            email='patricia.lima@equiny.dev',
            bio='Organizo encontros e eventos equestres locais. Bora fortalecer a comunidade.',
            phone='41992341111',
            avatar=ImageFaker.fake_dto(key='patricia.lima@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
        OwnersFaker.fake(
            name='Gustavo Barros',
            email='gustavo.barros@equiny.dev',
            bio='Criador e competidor amador. Curto conversar sobre genética, treino e provas.',
            phone='31970011223',
            avatar=ImageFaker.fake_dto(key='fernanda.ribeiro@equiny.dev.jpg'),
            has_completed_onboarding=True,
        ),
    ]

    def __init__(
        self, horses_repository: HorsesRepository, owners_repository: OwnersRepository
    ) -> None:
        self._horses_repository = horses_repository
        self._owners_repository = owners_repository

    def seed(self, accounts_ids: list[Id]) -> list[Id]:
        owners = self._seed_owners(accounts_ids)
        self._seed_horsers(owners)
        return [horse['horse'].id for horse in self._HORSES]

    def _seed_owners(self, accounts_ids: list[Id]) -> list[Owner]:
        owners: list[Owner] = []
        for index, owner in enumerate(self._OWNERS):
            owner.account_id = accounts_ids[index]
            owners.append(owner)
        self._owners_repository.add_many(owners)
        return owners

    def _seed_horsers(self, owners: list[Owner]) -> None:
        for index, horse_data in enumerate(self._HORSES):
            self._horses_repository.add(horse_data['horse'], owners[index].id)
            self._horses_repository.add_many_images(
                horse_data['horse'].id, horse_data['images']
            )
