from enum import Enum


class Signal(Enum):
    BUY = 1
    SELL = -1
    NO_ACTION = 0

    def __str__(self):
        return self.value