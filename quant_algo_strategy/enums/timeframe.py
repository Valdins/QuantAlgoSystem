from enum import Enum


class Timeframe(Enum):
    MIN_1 = 0
    MIN_15 = 1
    HOUR_1 = 2
    DAY_1 = 3

    def __str__(self):
        return self.value