from typing import Optional

from pydantic import BaseModel, Field


class FolderSchema(BaseModel):
    name: str = Field(min_length=1, max_length=96)


class FileSchema(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=96)
    folder_id: Optional[str] = Field(default=None)
