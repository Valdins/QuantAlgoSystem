from typing import Dict, Any
import pandas as pd


class MarketDataManager:
    def __init__(self):
        self.data = pd.DataFrame(columns=[
            'timestamp', 'bid', 'high', 'low', 'close', 'volume',
            'symbol', 'ask', 'bid_qty', 'ask_qty', 'last', 'vwap',
            'change', 'change_pct'
        ])
        self.data.set_index('timestamp', inplace=True)
        self.data_limit_1_min = 120 # 2h limit

    def process_latest_market_data(self, market_data: Dict[str, Any]) -> pd.DataFrame:
        # Convert timestamp string to datetime if needed
        print("Processing latest market data")
        if isinstance(market_data['timestamp'], str):
            market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])

        # Create a new DataFrame with the latest data
        new_data = pd.DataFrame([market_data])
        new_data.set_index('timestamp', inplace=True)

        # Append new data to existing DataFrame
        self.data = pd.concat([self.data, new_data])

        # Keep latest 120 records
        self.data = self.data[-self.data_limit_1_min:]

        print(f"Data contains {len(self.data)} entries")

        return self.data

    def get_latest_data(self) -> pd.DataFrame:
        return self.data.tail(1)


class PositionsDataManager:
    def __init__(self):
        self.data = {
            "initial_capital": 0,
            "current_capital": 0,
            "total_return_pct": 0.0,
            "total_profit": 0,
            "unrealized_pnl": 0,
            "open_positions": 0,
            "total_positions": 0,
            "winning_positions": 0,
            "win_rate_pct": 0,
            "positions_by_strategy": {}
        }

    def process_latest_positions_data(self, positions_data: Dict[str, Any]) -> Dict[str, Any]:
        # Convert timestamp string to datetime if needed
        print("Processing latest positions data")

        self.data = positions_data

        return self.data

    def get_latest_data(self) -> Dict[str, Any]:
        return self.data

# {
#     "initial_capital": 1000,
#     "current_capital": 1000,
#     "total_return_pct": 0.0,
#     "total_profit": 0,
#     "unrealized_pnl": 0,
#     "open_positions": 0,
#     "total_positions": 0,
#     "winning_positions": 0,
#     "win_rate_pct": 0,
#     "positions_by_strategy": {}
# }


# {
# 	"timestamp": "2023-07-12T18:03:00",
# 	"bid": 30772.0,
# 	"high": 30772.0,
# 	"low": 30755.0,
# 	"close": 30755.0,
# 	"volume": 0.70396318,
# 	"symbol": "BTC/USD",
# 	"ask": 30772.0,
# 	"bid_qty": 0,
# 	"ask_qty": 0,
# 	"last": 0,
# 	"vwap": 0,
# 	"change": 0,
# 	"change_pct": 0
# }