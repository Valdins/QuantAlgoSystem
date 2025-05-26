from abc import ABC

import pandas as pd

class BacktesterHelper(ABC):

    @staticmethod
    def transform_kaggle_btc_data(data: pd.DataFrame, years_of_data: int = 2):
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