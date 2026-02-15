from pydantic import BaseModel


class ImageSchema(BaseModel):
    key: str
    name: str


class GalerySchema(BaseModel):
    images: list[ImageSchema]
