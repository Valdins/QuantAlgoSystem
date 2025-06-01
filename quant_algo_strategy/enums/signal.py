from enum import Enum


class Signal(Enum):
    SELL = -1
    NO_ACTION = 0
    BUY = 1

    def __str__(self):
        return self.value