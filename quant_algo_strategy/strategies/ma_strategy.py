import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from quant_algo_strategy.enums.signal import Signal
from quant_algo_strategy.strategies import Strategy


class MovingAverageStrategy(Strategy):
    """
    A simple moving average crossover strategy.
    """

    def __init__(self, short_window=20, long_window=50):
        """
        Initialize the moving average strategy.

        Args:
            short_window (int): Short moving average window
            long_window (int): Long moving average window
        """
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window

    def update_data(self, latest_data: pd.DataFrame):
        """Update strategy with new candle data"""
        self.data = pd.concat([self.data, latest_data])

        # Keep only the necessary history
        max_period = max(self.short_window, self.long_window)
        if len(self.data) > max_period * 2:
            self.data = self.data.iloc[-max_period * 2:]

    def generate_signal(self, data: pd.DataFrame) -> Signal:
        if len(self.data) < self.long_window:
            return Signal.NO_ACTION

        self.data['short_ma'] = self.data['last'].rolling(self.short_window).mean()
        self.data['long_ma'] = self.data['last'].rolling(self.long_window).mean()

        # Check for crossover
        last_row = self.data.iloc[-1]
        prev_row = self.data.iloc[-2]

        if (prev_row['short_ma'] < prev_row['long_ma'] and
                last_row['short_ma'] > last_row['long_ma']):
            return Signal.BUY
        elif (prev_row['short_ma'] > prev_row['long_ma'] and
              last_row['short_ma'] < last_row['long_ma']):
            return Signal.SELL

        return Signal.NO_ACTION

    def process_latest_data(self, latest_data: pd.DataFrame):
        self.data = pd.concat([self.data, latest_data])


    def backtest(self):
        """
        Backtest the strategy and calculate performance metrics.

        Returns:
            dict: Dictionary with performance metrics
        """
        if self.signals is None:
            self.generate_signals()

        # Create a DataFrame for positions and portfolio value
        positions = pd.DataFrame(index=self.signals.index)
        positions['Position'] = self.signals['Signal']

        # Calculate daily returns
        positions['Returns'] = self.data['Close'].pct_change()

        # Calculate strategy returns
        positions['Strategy_Returns'] = positions['Position'].shift(1) * positions['Returns']

        # Calculate cumulative returns
        positions['Cumulative_Returns'] = (1 + positions['Returns']).cumprod()
        positions['Strategy_Cumulative_Returns'] = (1 + positions['Strategy_Returns']).cumprod()

        # Calculate performance metrics
        total_return = positions['Strategy_Cumulative_Returns'].iloc[-1] - 1
        annual_return = (positions['Strategy_Cumulative_Returns'].iloc[-1] ** (252 / len(positions))) - 1
        sharpe_ratio = np.sqrt(252) * (positions['Strategy_Returns'].mean() / positions['Strategy_Returns'].std())
        max_drawdown = (positions['Strategy_Cumulative_Returns'] / positions[
            'Strategy_Cumulative_Returns'].cummax() - 1).min()

        self.positions = positions

        # Return performance metrics
        metrics = {
            'Total Return': total_return,
            'Annual Return': annual_return,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown
        }

        return metrics

    def plot_performance(self):
        """
        Plot the performance of the strategy.
        """
        if self.positions is None:
            self.backtest()

        plt.figure(figsize=(12, 6))
        plt.plot(self.positions.index, self.positions['Cumulative_Returns'], label='Buy and Hold')
        plt.plot(self.positions.index, self.positions['Strategy_Cumulative_Returns'], label='Strategy')
        plt.title('Strategy Performance')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Returns')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_ma(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.data.index, self.data['Close'], label='Close Price')
        plt.plot(self.signals.index, self.signals['Short_MA'], label='Short MA')
        plt.plot(self.signals.index, self.signals['Long_MA'], label='Long MA')
        plt.title('Price and Moving Averages')
        plt.xlabel('Date')
        plt.ylabel('Moving averages')
        plt.legend()
        plt.grid(True)
        plt.show()