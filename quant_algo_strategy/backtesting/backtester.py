import logging
import time

import matplotlib.pyplot as plt

from quant_algo_strategy.data_processing.timeframe_manager import TimeframeManager
from quant_algo_strategy.positions.positions_manager import PositionManager
from quant_algo_strategy.data_processing.data_loader import DataLoader
from quant_algo_strategy.subscription import Subject
from quant_algo_strategy.strategies import Strategy
from quant_algo_strategy.enums import Signal


class Backtester(Subject):
    """
    Class for backtesting trading strategies.
    """
    def __init__(self, data_loader: DataLoader, strategy: Strategy):
        """
        Initialize the backtester.
        """
        super().__init__()
        self.strategy = strategy
        self.dataset = data_loader.load_data()
        self.results = []

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def run_backtest(self, position_manager: PositionManager, timeframe_manager: TimeframeManager):

        for index, row in self.dataset.iterrows():
            print(row)

            current_price = row['close']
            current_time = row['timestamp']

            # 1. Update timeframes with new tick
            completed_candles = timeframe_manager.process_tick(row)

            # 2. Check exit conditions for existing positions
            position_manager.check_exit_conditions(current_price, current_time)

            # 3. Process strategy for each completed candle
            strategy_timeframe = self.strategy.timeframe

            # Check if we have a new candle for this strategy's timeframe
            if completed_candles.get(strategy_timeframe):
                self.strategy.update_with_candle(completed_candles[strategy_timeframe])
                signal = self.strategy.generate_signal()

                if signal != Signal.NO_ACTION:
                    self.logger.info(f"Strategy {self.strategy.name} generated {signal} signal at {current_price}")

                    # 4. Execute trade through position manager
                    position_manager.process_signal(
                        signal=signal,
                        current_price=current_price,
                        current_time=current_time,
                        strategy_name=self.strategy.name
                    )

            # 5. Periodic performance summary
            print(f"Summary of current positions: {position_manager.get_portfolio_summary()}")

            time.sleep(0.5)


    def compare_strategies(self) -> None:
        """
        Compare the performance of all backtested strategies.
        """
        if not self.results:
            print("No backtest results to compare.")
            return

        plt.figure(figsize=(12, 6))

        for result in self.results:
            plt.plot(
                result.positions.index, 
                result.positions['Strategy_Cumulative_Returns'], 
                label=result.strategy_name
            )

        # Also plot buy and hold from the first result
        plt.plot(
            self.results[0].positions.index, 
            self.results[0].positions['Cumulative_Returns'], 
            label='Buy and Hold'
        )

        plt.title('Strategy Comparison')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Returns')
        plt.legend()
        plt.grid(True)
        plt.show()
