from pydantic import Field


name_schema = Field(min_length=3, max_length=100)
