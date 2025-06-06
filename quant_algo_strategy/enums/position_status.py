from enum import Enum


class PositionStatus(Enum):
    CLOSED = 0
    OPEN = 1

    def __str__(self):
        return self.value