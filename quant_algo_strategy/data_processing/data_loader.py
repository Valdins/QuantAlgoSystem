from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd

from quant_algo_strategy.backtesting import BacktesterHelper


class DataLoader(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def load_data(self):
        pass


class YFinanceDataLoader(DataLoader):
    def __init__(self, asset_name: str, start_date: datetime, end_date: datetime):
        super().__init__()
        self.asset_name = asset_name
        self.start_date = start_date.strftime('%Y-%m-%d')
        self.end_date = end_date.strftime('%Y-%m-%d')

    def load_data(self):
        import yfinance as yf
        data = yf.download(self.asset_name, start=self.start_date, end=self.end_date)
        return data

class KaggleDataLoader(DataLoader):
    def __init__(self):
        super().__init__()

    def load_data(self):
        file_path = str(Path(__file__).parent.parent / "data" / "btcusd_1-min_data.csv")

        raw_btc_historical_data_df = pd.read_csv(file_path)

        btc_historical_data_df = BacktesterHelper.transform_kaggle_btc_data(raw_btc_historical_data_df)

        return btc_historical_data_df