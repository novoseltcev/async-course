from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    '''Base orm object to register metadata'''


class IDMixin(Base):
    '''Single PK as id'''

    __abstract__ = True

    id_: Mapped[int] = mapped_column('id', primary_key=True, index=True)


class InternalEntityMixin(IDMixin):
    __abstract__ = True

    pid: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        default=uuid4,
        server_default=sa.text('gen_random_uuid()'),
        unique=True,
    )


class TimestampMixin(Base):
    '''System labels about the entity and its life cycle'''

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=sa.func.now(), nullable=True)
