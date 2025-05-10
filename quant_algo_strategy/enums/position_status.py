from enum import Enum


class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"

    def __str__(self):
        return self.value