"""Validated records at application boundaries."""

from pydantic import BaseModel, ConfigDict, Field


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)


class Workspace(Record):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=120)
    revision: int = Field(ge=0)


class RenameWorkspace(Record):
    name: str = Field(min_length=1, max_length=120)
    expected_revision: int = Field(ge=0)


class ConflictDetail(Record):
    message: str
    current_revision: int = Field(ge=0)


class ConflictResponse(Record):
    detail: ConflictDetail
