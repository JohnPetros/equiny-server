from typing import Annotated
from pydantic import UUID4

IdSchema = Annotated[str, UUID4]
