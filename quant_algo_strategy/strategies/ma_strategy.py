import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from quant_algo_strategy.strategies import Strategy


class MovingAverageStrategy(Strategy):
    """
    A simple moving average crossover strategy.
    """

    def __init__(self, data, short_window=20, long_window=50):
        """
        Initialize the moving average strategy.

        Args:
            data (pd.DataFrame): Market data with OHLCV format
            short_window (int): Short moving average window
            long_window (int): Long moving average window
        """
        super().__init__(data)
        self.short_window = short_window
        self.long_window = long_window
        self.signals = None
        self.positions = None
        self.returns = None

    def generate_signals(self):
        """
        Generate trading signals based on moving average crossover.

        Returns:
            pd.DataFrame: DataFrame with signals
        """
        signals = pd.DataFrame(index=self.data.index)
        signals['Signal'] = 0.0

        # Create short and long moving averages
        signals['Short_MA'] = self.data['Close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['Long_MA'] = self.data['Close'].rolling(window=self.long_window, min_periods=1).mean()

        # Create signals
        signals['Signal'][self.short_window:] = np.where(
            signals['Short_MA'][self.short_window:] > signals['Long_MA'][self.short_window:], 1.0, 0.0)

        # Generate trading orders
        signals['Position'] = signals['Signal'].diff()

        self.signals = signals
        return signals

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