from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    '''Base orm object to register metadata'''


class UUIDMixin(Base):
    '''Single PK as uuid'''

    __abstract__ = True

    uuid: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        default=uuid4,
        server_default=sa.text('gen_random_uuid()'),
        primary_key=True,
        index=True,
    )


class TimestampMixin(Base):
    '''System labels about the entity and its life cycle'''

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=sa.func.now(), nullable=True)
