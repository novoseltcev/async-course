from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pid: UUID
    description: str
    assignee: UUID
    fee: float
    award: float


class PostSchema(BaseModel):
    description: str
