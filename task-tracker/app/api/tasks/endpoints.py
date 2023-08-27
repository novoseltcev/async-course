from random import randint
from typing import Annotated
from uuid import UUID, uuid4

import sqlalchemy as sa
from confluent_kafka import Producer
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.db import AsyncSession, get_session
from app.kafka import get_producer
from app.models.entities import Account, Task
from app.models.enums import Role
from app.models.events import (
    AddedTaskBE,
    AddedTaskData,
    CompletedTaskBE,
    CompletedTaskData,
    CreatedTaskCUD,
    CreatedTaskData,
    EventMeta,
    ReshaffledTaskBE, ReshaffledTaskData
)

from .schemas import GetSchema, PostSchema

router = APIRouter()


@router.get('/')
async def get_tasks(
    _: Annotated[Account, Depends(get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
) -> list[GetSchema]:
    result = await db_session.execute(sa.select(Task))
    tasks = result.scalars().all()
    return [GetSchema.model_validate(task, from_attributes=True) for task in tasks]


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_task(
    body: PostSchema,
    me: Annotated[Account, Depends(get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
    producer: Annotated[Producer, Depends(get_producer)],
) -> None:
    if me.role not in [Role.admin, Role.manager]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    result = await db_session.execute(sa.select(Account))
    accounts = result.scalars().all()
    task = Task(
        pid=uuid4(),
        **body.model_dump(),
        fee=randint(10, 20),  # noqa: S311
        award=randint(20, 40),  # noqa: S311
        assignee=accounts[randint(0, len(accounts) - 1)],  # noqa: S311
    )
    db_session.add(task)

    event = CreatedTaskCUD(
        meta=EventMeta(name='Tasks.Created'),
        data=CreatedTaskData.model_validate(task),
    )
    producer.produce(
        topic='tasks-stream',
        value=event.model_dump_json(),
    )
    producer.flush()
    event = AddedTaskBE(
        meta=EventMeta(name='Tasks.Added'),
        data=AddedTaskData.model_validate(task),
    )
    producer.produce(
        topic='tasks.added',
        value=event.model_dump_json(),
    )
    await db_session.commit()


@router.put('/{pid}/complete', status_code=status.HTTP_204_NO_CONTENT)
async def mark_task_completed(
    pid: UUID,
    me: Annotated[Account, Depends(get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
    producer: Annotated[Producer, Depends(get_producer)],
) -> None:
    result = await db_session.execute(sa.select(Task).where(Task.pid == pid))
    task = result.scalar()
    if not task or task.assignee != me.pid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task.completed = True
    await db_session.flush([task])
    event = CompletedTaskBE(
        meta=EventMeta(name='Tasks.Completed'),
        data=CompletedTaskData.model_validate(task, from_attributes=True),
    )
    producer.produce(
        topic='tasks.completed',
        value=event.model_dump_json(),
    )
    producer.flush()
    await db_session.commit()


@router.post('/reshaffle', status_code=status.HTTP_204_NO_CONTENT)
async def _(
    me: Annotated[Account, Depends(get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
    producer: Annotated[Producer, Depends(get_producer)],
) -> None:
    if me.role not in [Role.admin, Role.manager]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    tasks = (await db_session.execute(sa.select(Task))).scalars().all()
    accounts = (await db_session.execute(sa.select(Task))).scalars().all()
    for task in tasks:
        task.assignee = accounts[randint(0, len(accounts) - 1)].pid  # noqa: S311

    await db_session.flush(tasks)
    for task in tasks:
        event = ReshaffledTaskBE(
            meta=EventMeta(name='Tasks.Reshaffled'),
            data=ReshaffledTaskData.model_validate(task, from_attributes=True),
        )
        producer.produce(
            topic='tasks.reshaffled',
            value=event.model_dump_json(),
        )
    producer.flush()
    await db_session.commit()
