from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Role


class EventMeta(BaseModel):
    created_at: int = Field(default_factory=lambda: datetime.now(UTC).timestamp())
    name: str


T = TypeVar('T', bound=BaseModel)


class BaseEvent(BaseModel, Generic[T]):
    meta: EventMeta
    data: T


class CreatedTaskData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pid: UUID
    description: str
    assignee: UUID
    fee: float
    award: float


class CreatedTaskCUD(BaseEvent[CreatedTaskData]):
    '''CUD Event produced on Task created'''


class AddedTaskData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pid: UUID
    assignee: UUID
    fee: float


class AddedTaskBE(BaseEvent[AddedTaskData]):
    '''BE Event produced on Task added'''


class ReshaffledTaskData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pid: UUID
    assignee: UUID
    fee: float


class ReshaffledTaskBE(BaseEvent[ReshaffledTaskData]):
    '''BE Event produced on Task reshaffled'''


class CompletedTaskData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pid: UUID
    assignee: UUID
    award: float


class CompletedTaskBE(BaseEvent[CompletedTaskData]):
    '''BE Event produced on Task completed'''


class CreateAccountData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pid: UUID
    role: Role
    email: str


class CreateAccountCUD(BaseEvent[CreateAccountData]):
    '''CUD Event produced on account creation'''
