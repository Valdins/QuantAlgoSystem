from abc import ABC, abstractmethod

from datetime import datetime

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