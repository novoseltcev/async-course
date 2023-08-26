from enum import StrEnum, auto


class Role(StrEnum):
    worker = auto()
    bookkeeper = auto()
    manager = auto()
    admin = auto()
