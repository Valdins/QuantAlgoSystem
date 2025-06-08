from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd


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

        btc_historical_data_df = self._transform_kaggle_btc_data(raw_btc_historical_data_df)

        return btc_historical_data_df


    def _transform_kaggle_btc_data(self, data: pd.DataFrame, years_of_data: int = 2):
        data.rename(columns={'Timestamp': 'timestamp', 'Open': 'bid', 'High': 'high', 'Low': 'low', 'Close': 'close',
                             'Volume': 'volume'}, inplace=True)
        data['symbol'] = 'BTC/USD'
        data['ask'] = data['bid']
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s')

        data['bid_qty'] = 0
        data['ask_qty'] = 0
        data['last'] = 0
        data['vwap'] = 0
        data['change'] = 0
        data['change_pct'] = 0

        years_ago = pd.Timestamp.now() - pd.DateOffset(years=years_of_data)
        data = data[data['timestamp'] >= years_ago]
        return data