from pydantic import Field
from typing import Annotated

NameSchema = Annotated[str, Field(min_length=3, max_length=100)]
