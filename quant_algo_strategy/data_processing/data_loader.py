from abc import ABC, abstractmethod


class DataLoader(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def load_data(self):
        pass

class YFinanceDataLoader(DataLoader):
    def __init__(self, asset_name, start_date, end_date):
        super().__init__()
        self.asset_name = asset_name
        self.start_date = start_date
        self.end_date = end_date

    def load_data(self):
        import yfinance as yf
        data = yf.download(self.asset_name, start=self.start_date, end=self.end_date)
        return data
