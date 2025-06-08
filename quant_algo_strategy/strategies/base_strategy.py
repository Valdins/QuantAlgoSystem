from abc import ABC, abstractmethod

import pandas as pd

from quant_algo_strategy.enums import Timeframe


class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    """
    def __init__(self, dataset: pd.DataFrame, timeframe: Timeframe, strategy_name: str):
        self._timeframe = timeframe
        self.data = dataset,
        self._strategy_name = strategy_name

    @property
    def name(self):
        return self._strategy_name

    @property
    def timeframe(self):
        return self._timeframe

    @abstractmethod
    def update_with_candle(self, data: pd.DataFrame):
        pass

    @abstractmethod
    def generate_signal(self):
        pass

    @abstractmethod
    def backtest(self):
        pass