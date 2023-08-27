import asyncio

import sqlalchemy as sa
from confluent_kafka import Consumer

from app.db import get_session
from app.models.entities import Account
from app.models.events import CreateAccountCUD
from app.settings import get_settings

consumer = Consumer({'bootstrap.servers': get_settings().kafka.URI})
consumer.subscribe(['accounts-stream'])


async def loop() -> None:
    db_session = await get_session().__anext__()
    while True:
        msg = consumer.poll(10)
        if msg is None:
            continue

        if msg.error():
            print(f'Consumer error: {msg.error()}')
            continue

        event = CreateAccountCUD.model_validate_json(msg.value())

        account = (
            await db_session.execute(
                sa.select(Account).where(Account.pid == event.data.pid),
            )
        ).scalar()
        if account:
            account.role = event.data.role
            await db_session.flush([account])
            continue

        db_session.add(
            Account(
                pid=event.data.pid,
                role=event.data.role,
            ),
        )
        await db_session.commit()


def start_consumer() -> None:
    asyncio.run(loop())
