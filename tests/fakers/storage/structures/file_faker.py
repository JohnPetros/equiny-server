from faker import Faker

from equiny.core.storage.structures.dtos import FileDto
from equiny.core.storage.structures.file import File


class FileFaker:
    _faker = Faker()

    @staticmethod
    def fake_dto(
        name: str | None = None,
        folder: str = 'images',
        data: bytes | None = None,
        content_type: str = 'image/jpeg',
    ) -> FileDto:
        return FileDto(
            name=name or f'{FileFaker._faker.uuid4()}.jpg',
            folder=folder,
            data=data or b'fake-image-data',
            content_type=content_type,
        )

    @staticmethod
    def fake() -> File:
        return File.create(FileFaker.fake_dto())

    @staticmethod
    def fake_many(
        count: int,
        content_type: str = 'image/jpeg',
    ) -> list[FileDto]:
        return [
            FileFaker.fake_dto(
                name=f'image_{i}.jpg',
                content_type=content_type,
            )
            for i in range(count)
        ]
