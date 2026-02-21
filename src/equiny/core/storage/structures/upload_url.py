from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures import Text
from equiny.core.shared.domain.structures.url import Url
from equiny.core.storage.structures.dtos.upload_url_dto import UploadUrlDto


@structure
class UploadUrl(Structure):
    url: Url
    token: Text
    file_path: Text

    @classmethod
    def create(cls, dto: UploadUrlDto) -> 'UploadUrl':
        return cls(
            url=Url.create(dto.url),
            token=Text.create(dto.token),
            file_path=Text.create(dto.file_path),
        )

    @property
    def dto(self) -> UploadUrlDto:
        return UploadUrlDto(
            url=self.url.value,
            token=self.token.value,
            file_path=self.file_path.value,
        )
