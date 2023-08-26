from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr

from app.models.enums import Role


class GetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pid: UUID
    username: str
    email: EmailStr
    role: Role


class PutSchema(BaseModel):
    email: EmailStr
    role: Role


class PostSchema(BaseModel):
    username: str
    password: SecretStr
    email: EmailStr
    role: Role
