from typing import Annotated
from uuid import UUID, uuid4

import sqlalchemy as sa
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field

from app.db import AsyncSession, get_session
from app.models.entities import AuthorizedService

router = APIRouter()


class ServiceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id_: Annotated[UUID, Field(alias='id')]
    secret: UUID


@router.get('/', response_model=list[ServiceSchema])
async def get_all_services(
    db_session: Annotated[AsyncSession, Depends(get_session)],
) -> list:
    result = await db_session.execute(sa.select(AuthorizedService))
    return [ServiceSchema.model_validate(service) for service in result.scalars().all()]


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ServiceSchema)
async def create_service(
    db_session: Annotated[AsyncSession, Depends(get_session)],
) -> ServiceSchema:
    service = AuthorizedService(secret=uuid4())
    db_session.add(service)
    await db_session.commit()
    return ServiceSchema.model_validate(service)
