from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .enums import Role
from .mixins import ExternalEntityMixin, InternalEntityMixin


class Account(ExternalEntityMixin):
    __tablename__ = 'accounts'

    role: Mapped[Role] = mapped_column(default=Role.worker)


class Task(InternalEntityMixin):
    __tablename__ = 'tasks'

    description: Mapped[str] = mapped_column()
    completed: Mapped[bool] = mapped_column(default=False)
    fee: Mapped[float] = mapped_column()
    award: Mapped[float] = mapped_column()
    assignee: Mapped[UUID] = mapped_column(sa.ForeignKey('accounts.pid'))
