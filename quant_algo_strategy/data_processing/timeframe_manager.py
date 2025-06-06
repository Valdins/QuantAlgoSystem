from collections import deque
from datetime import datetime
from typing import Optional, Dict

import pandas as pd


class TimeframeManager:
    """
    Manages different timeframes for trading data aggregation.
    Converts second-by-second data into higher timeframes (1min, 5min, 15min, etc.)
    """

    def __init__(self):
        self.timeframes = {
            '1m': {'seconds': 60, 'data': deque(), 'current_candle': None},
            '5m': {'seconds': 300, 'data': deque(), 'current_candle': None},
            '15m': {'seconds': 900, 'data': deque(), 'current_candle': None},
            '1h': {'seconds': 3600, 'data': deque(), 'current_candle': None}
        }

    def process_tick(self, tick_data: dict) -> Dict[str, Optional[dict]]:
        """
        Process incoming tick data and update all timeframes.

        Args:
            tick_data: Dict with structure like your example

        Returns:
            Dict of completed candles for each timeframe (None if no new candle)
        """
        timestamp = datetime.now()  # Or parse from tick_data if available
        completed_candles = {}

        for tf_name, tf_config in self.timeframes.items():
            completed_candle = self._update_timeframe(
                tf_name, tf_config, tick_data, timestamp
            )
            completed_candles[tf_name] = completed_candle

        return completed_candles

    def _update_timeframe(self, tf_name: str, tf_config: dict,
                          tick_data: dict, timestamp: datetime) -> Optional[dict]:
        """Update a specific timeframe and return completed candle if any."""

        # Calculate candle start time
        seconds_in_tf = tf_config['seconds']
        candle_start = self._get_candle_start_time(timestamp, seconds_in_tf)

        current_candle = tf_config['current_candle']

        # Check if we need to start a new candle
        if (current_candle is None or
                current_candle['timestamp'] != candle_start):

            # Save the completed candle
            completed_candle = None
            if current_candle is not None:
                completed_candle = current_candle.copy()
                tf_config['data'].append(completed_candle)

                # Keep only last 200 candles to manage memory
                if len(tf_config['data']) > 200:
                    tf_config['data'].popleft()

            # Start new candle
            tf_config['current_candle'] = {
                'timestamp': candle_start,
                'open': tick_data['last'],
                'high': tick_data['last'],
                'low': tick_data['last'],
                'close': tick_data['last'],
                'volume': tick_data['volume'],
                'symbol': tick_data['symbol']
            }

            return completed_candle

        else:
            # Update current candle
            current_candle['high'] = max(current_candle['high'], tick_data['last'])
            current_candle['low'] = min(current_candle['low'], tick_data['last'])
            current_candle['close'] = tick_data['last']
            current_candle['volume'] = tick_data['volume']  # Or accumulate if needed

            return None

    def _get_candle_start_time(self, timestamp: datetime, seconds: int) -> datetime:
        """Get the start time of the candle for given timestamp and timeframe."""
        total_seconds = int(timestamp.timestamp())
        candle_seconds = (total_seconds // seconds) * seconds
        return datetime.fromtimestamp(candle_seconds)

    def get_dataframe(self, timeframe: str, periods: int = 100) -> pd.DataFrame:
        """
        Get pandas DataFrame for a specific timeframe.

        Args:
            timeframe: '1m', '5m', '15m', '1h'
            periods: Number of recent periods to return

        Returns:
            pandas DataFrame with OHLCV data
        """
        if timeframe not in self.timeframes:
            raise ValueError(f"Timeframe {timeframe} not supported")

        candles = list(self.timeframes[timeframe]['data'])[-periods:]

        if not candles:
            return pd.DataFrame()

        df = pd.DataFrame(candles)
        df.set_index('timestamp', inplace=True)
        return df