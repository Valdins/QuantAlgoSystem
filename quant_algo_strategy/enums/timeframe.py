from enum import Enum


class Timeframe(Enum):
    MIN_1 = '1m'
    MIN_5 = '5m'
    MIN_15 = '15m'
    HOUR_1 = '1h'
    DAY_1 = '1day'

    def __str__(self):
        return self.value