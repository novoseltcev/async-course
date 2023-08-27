from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import get_settings

engine = create_async_engine(
    str(get_settings().db.URI),
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
