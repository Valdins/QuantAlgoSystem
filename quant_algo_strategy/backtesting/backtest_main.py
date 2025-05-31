from quant_algo_strategy.data_processing.data_loader import KaggleDataLoader
from quant_algo_strategy.strategies import MovingAverageStrategy
from quant_algo_strategy.positions import PositionsManager
from quant_algo_strategy.backtesting import Backtester


def main():
    position_manager = PositionsManager()
    ma_strategy = MovingAverageStrategy(short_window=20, long_window=50)
    data_loader = KaggleDataLoader()
    backtester = Backtester(data_loader, ma_strategy)

    backtester.run_backtest(position_manager)


if __name__ == "__main__":
    main()
