from pydantic import BaseModel, Field


class FolderSchema(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class FileSchema(BaseModel):
    name: str = Field(min_length=1, max_length=50)
