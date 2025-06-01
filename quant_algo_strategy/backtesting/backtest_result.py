from typing import Dict

from matplotlib import pyplot as plt
import pandas as pd


class BacktestResult:
    """
    Class to store and analyze backtest results.
    """
    def __init__(self, strategy_name: str, metrics: Dict[str, float], positions: pd.DataFrame, strategy=None):
        """
        Initialize the backtest result.

        Args:
            strategy_name: Name of the strategy
            metrics: Performance metrics
            positions: DataFrame with positions and returns
            strategy: Reference to the strategy object
        """
        self.strategy_name = strategy_name
        self.metrics = metrics
        self.positions = positions
        self.strategy = strategy

    def print_metrics(self) -> None:
        """
        Print the performance metrics.
        """
        print(f"Performance Metrics for {self.strategy_name}:")
        for metric, value in self.metrics.items():
            print(f"{metric}: {value:.4f}")

    def plot_performance(self) -> None:
        """
        Plot the performance of the strategy.

        If the strategy has a plot_performance method, it will be used.
        Otherwise, a default plot will be generated.
        """
        if self.strategy and hasattr(self.strategy, 'plot_performance'):
            # Use the strategy's plot_performance method
            # First, ensure the strategy's positions are up to date
            self.strategy.positions = self.positions

            # Call the strategy's plot_performance method
            self.strategy.plot_performance()

            self.strategy.plot_ma()
        else:
            # Fall back to the default implementation
            plt.figure(figsize=(12, 6))
            plt.plot(self.positions.index, self.positions['Cumulative_Returns'], label='Buy and Hold')
            plt.plot(self.positions.index, self.positions['Strategy_Cumulative_Returns'], label=self.strategy_name)
            plt.title(f'{self.strategy_name} Performance')
            plt.xlabel('Date')
            plt.ylabel('Cumulative Returns')
            plt.legend()
            plt.grid(True)
            plt.show()