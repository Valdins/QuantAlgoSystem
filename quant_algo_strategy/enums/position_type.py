from enum import Enum


class PositionType(Enum):
    FLAT = 0
    LONG = 1
    SHORT = -1

    def __str__(self):
        return self.value