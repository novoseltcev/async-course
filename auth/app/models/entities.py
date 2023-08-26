from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .enums import Role
from .mixins import Base, InternalEntityMixin, TimestampMixin


class Account(InternalEntityMixin, TimestampMixin):
    __tablename__ = 'accounts'

    username: Mapped[str] = mapped_column(unique=True)
    encrypted_password: Mapped[str] = mapped_column()

    email: Mapped[str] = mapped_column()
    role: Mapped[Role] = mapped_column(default=Role.worker)


class AuthorizedService(Base):
    __tablename__ = 'authorized_services'

    id_: Mapped[UUID] = mapped_column(
        'id',
        sa.UUID(as_uuid=True),
        default=uuid4,
        server_default=sa.text('gen_random_uuid()'),
        primary_key=True,
    )

    secret: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        unique=True,
    )
