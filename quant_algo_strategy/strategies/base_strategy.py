from abc import ABC, abstractmethod
from typing import Dict, Any

import pandas as pd

from quant_algo_strategy.enums import Timeframe


class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    """
    def __init__(self, timeframe: Timeframe, strategy_name: str):
        self._timeframe = timeframe
        self._strategy_name = strategy_name
        self.data = pd.DataFrame({
            'timestamp': pd.Series(dtype='datetime64[ns]'),
            'open': pd.Series(dtype='float64'),
            'high': pd.Series(dtype='float64'),
            'low': pd.Series(dtype='float64'),
            'close': pd.Series(dtype='float64'),
            'volume': pd.Series(dtype='float64'),
            'symbol': pd.Series(dtype='str')
        })

    @property
    def name(self):
        return self._strategy_name

    @property
    def timeframe(self):
        return self._timeframe

    @abstractmethod
    def update_with_candle(self, data: Dict[str, Any]):
        pass

    @abstractmethod
    def generate_signal(self):
        pass

    @abstractmethod
    def backtest(self):
        pass