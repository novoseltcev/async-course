from typing import Annotated
from uuid import UUID, uuid4

import sqlalchemy as sa
from confluent_kafka import Producer
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from app.api.v1.deps import get_current_user
from app.db import AsyncSession, get_session
from app.kafka import get_producer
from app.models.entities import Account
from app.models.events import (
    CreateAccountCUD,
    CreateAccountData,
    DeleteAccountCUD,
    DeleteAccountData,
    EventMeta,
    UpdateAccountCUD,
    UpdateAccountData,
)

from .schemas import GetSchema, PostSchema, PutSchema

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

router = APIRouter()


@router.get('/')
async def get_accounts(
    _: Annotated[Account, Depends(get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
) -> list[GetSchema]:
    result = await db_session.execute(sa.select(Account))
    accounts = result.scalars().all()
    return [
        GetSchema.model_validate(account, from_attributes=True) for account in accounts
    ]


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_account(
    body: PostSchema,
    db_session: Annotated[AsyncSession, Depends(get_session)],
    producer: Annotated[Producer, Depends(get_producer)],
) -> None:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    account = Account(
        pid=uuid4(),
        username=body.username,
        encrypted_password=pwd_context.hash(body.password.get_secret_value()),
        email=body.email,
        role=body.role,
    )
    db_session.add(account)
    event = CreateAccountCUD(
        meta=EventMeta(name='Accounts.CreateAccount'),
        data=CreateAccountData.model_validate(account),
    )
    producer.produce(
        topic='accounts-stream',
        value=event.model_dump_json(),
    )
    producer.flush()
    await db_session.commit()


@router.put('/{pid}', status_code=status.HTTP_204_NO_CONTENT)
async def _(
    pid: UUID,
    body: PutSchema,
    _: Annotated[Account, Depends(get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
    producer: Annotated[Producer, Depends(get_producer)],
) -> None:
    await db_session.execute(
        sa.update(Account).where(Account.pid == pid).values(**body.model_dump()),
    )
    event = UpdateAccountCUD(
        meta=EventMeta(name='Accounts.UpdateAccount'),
        data=UpdateAccountData(
            pid=pid,
            email=body.email,
            role=body.role,
        ),
    )
    producer.produce(
        topic='accounts-stream',
        value=event.model_dump_json(),
    )
    producer.flush()
    await db_session.commit()


@router.delete('/{pid}', status_code=status.HTTP_204_NO_CONTENT)
async def _(
    pid: UUID,
    me: Annotated[Account, Depends(get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)],
    producer: Annotated[Producer, Depends(get_producer)],
) -> None:
    if pid == me.pid:
        raise HTTPException(status.HTTP_409_CONFLICT, detail='Нельзя удалить себя же')

    await db_session.execute(sa.delete(Account).where(Account.pid == pid))
    event = DeleteAccountCUD(
        meta=EventMeta(name='Accounts.DeleteAccount'),
        data=DeleteAccountData(pid=pid),
    )
    producer.produce(
        topic='accounts-stream',
        value=event.model_dump_json(),
    )
    producer.flush()
    await db_session.commit()
