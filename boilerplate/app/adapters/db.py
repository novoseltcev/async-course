from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import get_settings

if not (DATABASE_URI := get_settings().SQLALCHEMY_DATABASE_URI):
    msg = "You're should set `SQLALCHEMY_DATABASE_URI` on .env file"
    raise ValueError(msg)

engine = create_async_engine(
    str(DATABASE_URI),
    pool_pre_ping=True,
)

maker = async_sessionmaker[AsyncSession](
    engine,
    autoflush=False,
    expire_on_commit=False,
    autocommit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with maker() as session:
        yield session
