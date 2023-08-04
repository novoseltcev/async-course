from .mixins import TimestampMixin, UUIDMixin


class Account(UUIDMixin, TimestampMixin):
    __tablename__ = 'accounts'
