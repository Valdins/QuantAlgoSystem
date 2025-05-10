from enum import Enum


class PositionType(Enum):
    LONG = "long"
    SHORT = "short"

    def __str__(self):
        return self.value