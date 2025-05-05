import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from quant_algo_strategy.strategies import Strategy
from quant_algo_strategy.positions import PositionsManager


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


class AdvancedMovingAverageStrategy(Strategy):
    def __init__(self, data, short_window=15, take_profit_pct=4.0, stop_loss_pct=4.0):
        """
        Initialize the advanced moving average strategy with position management.

        Args:
            data (pd.DataFrame): Market data with OHLCV format
            short_window (int): Short moving average window
            take_profit_pct (float): Take profit percentage
            stop_loss_pct (float): Stop loss percentage
        """
        super().__init__(data)
        self.short_window = short_window
        self.signals = None
        self.positions = None
        self.returns = None
        self.positions_manager = PositionsManager(take_profit_pct, stop_loss_pct)

    def generate_signals(self):
        """
        Generate trading signals based on price relative to short moving average.
        Buy when price goes above short MA, short when price goes below short MA.

        Returns:
            pd.DataFrame: DataFrame with signals
        """
        signals = pd.DataFrame(index=self.data.index)
        signals['Signal'] = 0.0

        # Create short and long moving averages
        signals['Short_MA'] = self.data['Close'].rolling(window=self.short_window, min_periods=1).mean()

        test = self.data['Close'][self.short_window:]
        s_test = signals['Signal'][self.short_window:]


        # Create signals
        # Buy (1.0) when price is above short MA
        # Short (-1.0) when price is below short MA
        signals['Signal'][self.short_window:] = np.where(
            self.data[('Close', 'AAPL')][self.short_window:] > signals['Short_MA'][self.short_window:], 1.0, -1.0)

        # Generate trading orders
        signals['Position'] = signals['Signal'].diff()

        self.signals = signals
        return signals

    def backtest(self):
        """
        Backtest the strategy and calculate performance metrics.
        Uses PositionsManager to handle take profit and stop loss.

        Returns:
            dict: Dictionary with performance metrics
        """
        if self.signals is None:
            self.generate_signals()

        # Reset positions manager
        self.positions_manager = PositionsManager(
            take_profit_pct=self.positions_manager.take_profit_pct,
            stop_loss_pct=self.positions_manager.stop_loss_pct
        )

        # Create a DataFrame for positions and portfolio value
        positions = pd.DataFrame(index=self.signals.index)
        positions['Signal'] = self.signals['Signal']
        positions['Price'] = self.data['Close']
        positions['Returns'] = self.data['Close'].pct_change()
        positions['Strategy_Returns'] = 0.0
        positions['Position_Type'] = 'none'
        positions['Position_Active'] = False
        positions['Take_Profit'] = 0.0
        positions['Stop_Loss'] = 0.0

        # Initialize cumulative returns
        positions['Cumulative_Returns'] = (1 + positions['Returns']).cumprod()
        positions['Strategy_Cumulative_Returns'] = 1.0

        # Process each day
        for i in range(1, len(positions)):
            current_date = positions.index[i]
            current_price = positions['Price'][i]
            prev_date = positions.index[i-1]

            # Check existing positions for take profit/stop loss
            closed_positions = self.positions_manager.check_positions(current_price, current_date)

            # Process signals
            if positions['Signal'][i] == 1.0 and not positions['Position_Active'][i-1]:
                # Buy signal and no active position
                self.positions_manager.open_position(current_price, current_date, 'long')
                positions.loc[current_date, 'Position_Type'] = 'long'
                positions.loc[current_date, 'Position_Active'] = True
            elif positions['Signal'][i] == -1.0 and not positions['Position_Active'][i-1]:
                # Short signal and no active position
                self.positions_manager.open_position(current_price, current_date, 'short')
                positions.loc[current_date, 'Position_Type'] = 'short'
                positions.loc[current_date, 'Position_Active'] = True
            else:
                # Carry forward position status
                positions.loc[current_date, 'Position_Type'] = positions.loc[prev_date, 'Position_Type']
                positions.loc[current_date, 'Position_Active'] = (
                    positions.loc[prev_date, 'Position_Active'] and 
                    not any(p.exit_time == current_date for p in closed_positions)
                )

            # Calculate strategy returns
            if positions.loc[prev_date, 'Position_Type'] == 'long':
                positions.loc[current_date, 'Strategy_Returns'] = positions.loc[current_date, 'Returns']
            elif positions.loc[prev_date, 'Position_Type'] == 'short':
                positions.loc[current_date, 'Strategy_Returns'] = -positions.loc[current_date, 'Returns']

            # Update cumulative returns
            if i > 0:
                positions.loc[current_date, 'Strategy_Cumulative_Returns'] = (
                    positions.loc[prev_date, 'Strategy_Cumulative_Returns'] * 
                    (1 + positions.loc[current_date, 'Strategy_Returns'])
                )

        # Close any remaining positions at the end
        self.positions_manager.close_all_positions(
            positions['Price'].iloc[-1], 
            positions.index[-1]
        )

        # Get position summary
        position_summary = self.positions_manager.get_position_summary()

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
            'Max Drawdown': max_drawdown,
            'Win Rate (%)': position_summary['Win Rate (%)'],
            'Total Positions': position_summary['Total Positions'],
            'Total Profit (%)': position_summary['Total Profit (%)']
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
        """
        Plot the price and moving averages.
        """
        if self.signals is None:
            self.generate_signals()

        plt.figure(figsize=(12, 6))
        plt.plot(self.data.index, self.data['Close'], label='Close Price')
        plt.plot(self.signals.index, self.signals['Short_MA'], label='Short MA')

        # Plot buy signals (long positions)
        if self.positions is not None:
            long_entries = self.positions[
                (self.positions['Position_Type'] == 'long') & 
                (self.positions['Position_Type'].shift(1) != 'long')
            ]
            plt.scatter(
                long_entries.index, 
                self.data.loc[long_entries.index]['Close'], 
                marker='^', color='g', s=100, label='Buy Signal'
            )

            # Plot short signals
            short_entries = self.positions[
                (self.positions['Position_Type'] == 'short') & 
                (self.positions['Position_Type'].shift(1) != 'short')
            ]
            plt.scatter(
                short_entries.index, 
                self.data.loc[short_entries.index]['Close'], 
                marker='v', color='r', s=100, label='Short Signal'
            )

        plt.title('Price and Moving Averages')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.show()
