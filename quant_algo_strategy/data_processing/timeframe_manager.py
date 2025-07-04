from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import pandas as pd


class TimeframeManager:
    """
    Manages different timeframes for trading data aggregation.
    Converts lower timeframe data into higher timeframes (1min -> 5min -> 15min -> 1h)
    """

    def __init__(self):
        self.timeframes = {
            '1m': {'seconds': 60, 'data': deque(), 'current_candle': None},
            '5m': {'seconds': 300, 'data': deque(), 'current_candle': None},
            '15m': {'seconds': 900, 'data': deque(), 'current_candle': None},
            '1h': {'seconds': 3600, 'data': deque(), 'current_candle': None}
        }

        # Track what timeframe the input data is
        self.input_timeframe = None
        self.last_processed_time = None

    def process_tick(self, tick_data: dict) -> Dict[str, Optional[dict]]:
        """
        Process incoming tick data and update all timeframes.

        Args:
            tick_data: Dict with structure containing 'timestamp', 'open', 'high', 'low', 'close', 'volume'

        Returns:
            Dict of completed candles for each timeframe (None if no new candle)
        """
        # Handle different timestamp formats
        if isinstance(tick_data.get('timestamp'), str):
            timestamp = pd.to_datetime(tick_data['timestamp'])
        elif isinstance(tick_data.get('timestamp'), pd.Timestamp):
            timestamp = tick_data['timestamp']
        else:
            timestamp = datetime.now()

        # Auto-detect input timeframe if not set
        if self.input_timeframe is None:
            self._detect_input_timeframe(timestamp)

        completed_candles = {}

        # Process each timeframe
        for tf_name, tf_config in self.timeframes.items():
            # Only process timeframes that are >= input timeframe
            if self._should_process_timeframe(tf_name):
                completed_candle = self._update_timeframe(
                    tf_name, tf_config, tick_data, timestamp
                )
                completed_candles[tf_name] = completed_candle
            else:
                completed_candles[tf_name] = None

        self.last_processed_time = timestamp
        return completed_candles

    def _detect_input_timeframe(self, timestamp: datetime):
        """Auto-detect the input data timeframe based on timestamp intervals."""
        if self.last_processed_time is None:
            self.last_processed_time = timestamp
            return

        time_diff = (timestamp - self.last_processed_time).total_seconds()

        # Determine input timeframe based on time difference
        if time_diff <= 60:
            self.input_timeframe = '1m'
        elif time_diff <= 300:
            self.input_timeframe = '5m'
        elif time_diff <= 900:
            self.input_timeframe = '15m'
        else:
            self.input_timeframe = '1h'

    def _should_process_timeframe(self, timeframe: str) -> bool:
        """Check if we should process this timeframe based on input timeframe."""
        if self.input_timeframe is None:
            return True

        timeframe_hierarchy = ['1m', '5m', '15m', '1h']
        input_idx = timeframe_hierarchy.index(self.input_timeframe)
        current_idx = timeframe_hierarchy.index(timeframe)

        return current_idx >= input_idx

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

            # OHLC data format
            price = tick_data['close']

            tf_config['current_candle'] = {
                'timestamp': candle_start,
                'open': tick_data.get('open', price),
                'high': tick_data.get('high', price),
                'low': tick_data.get('low', price),
                'close': price,
                'volume': tick_data.get('volume', 0),
                'symbol': tick_data.get('symbol', '')
            }

            return completed_candle

        else:
            # Update current candle
            # OHLC data format - aggregate properly
            current_candle['high'] = max(current_candle['high'], tick_data.get('high', current_candle['high']))
            current_candle['low'] = min(current_candle['low'], tick_data.get('low', current_candle['low']))
            current_candle['close'] = tick_data['close']
            current_candle['volume'] += tick_data.get('volume', 0)

            return None

    def _get_candle_start_time(self, timestamp: datetime, seconds: int) -> datetime:
        """Get the start time of the candle for given timestamp and timeframe."""
        if isinstance(timestamp, pd.Timestamp):
            timestamp = timestamp.to_pydatetime()

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

        # Include current candle if it exists
        current_candle = self.timeframes[timeframe]['current_candle']
        if current_candle:
            candles.append(current_candle)

        if not candles:
            return pd.DataFrame()

        df = pd.DataFrame(candles)
        df.set_index('timestamp', inplace=True)
        return df

    def get_latest_candle(self, timeframe: str) -> Optional[dict]:
        """Get the latest completed candle for a timeframe."""
        if timeframe not in self.timeframes:
            return None

        data = self.timeframes[timeframe]['data']
        if data:
            return data[-1]
        return None

    def get_current_candle(self, timeframe: str) -> Optional[dict]:
        """Get the current (incomplete) candle for a timeframe."""
        if timeframe not in self.timeframes:
            return None

        return self.timeframes[timeframe]['current_candle']

    def get_candle_count(self, timeframe: str) -> int:
        """Get the number of completed candles for a timeframe."""
        if timeframe not in self.timeframes:
            return 0

        return len(self.timeframes[timeframe]['data'])

    def reset(self):
        """Reset all timeframes (useful for new backtests)."""
        for tf_config in self.timeframes.values():
            tf_config['data'].clear()
            tf_config['current_candle'] = None
        self.input_timeframe = None
        self.last_processed_time = None