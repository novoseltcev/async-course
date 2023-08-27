from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import Role


class EventMeta(BaseModel):
    created_at: int = Field(default_factory=lambda: datetime.now(UTC).timestamp())
    name: str


T = TypeVar('T', bound=BaseModel)


class BaseEvent(BaseModel, Generic[T]):
    meta: EventMeta
    data: T


class CreateAccountData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pid: UUID
    role: Role
    email: EmailStr


class CreateAccountCUD(BaseEvent[CreateAccountData]):
    '''CUD Event produced on account creation'''


class DeleteAccountData(BaseModel):
    pid: UUID


class DeleteAccountCUD(BaseEvent[DeleteAccountData]):
    '''CUD Event produced on account deletion'''


class UpdateAccountData(BaseModel):
    pid: UUID
    role: Role
    email: EmailStr


class UpdateAccountCUD(BaseEvent[UpdateAccountData]):
    '''CUD Event produced on account editing'''
