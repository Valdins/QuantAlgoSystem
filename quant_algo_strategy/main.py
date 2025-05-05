from datetime import datetime, timedelta
from data_processing import YFinanceDataLoader

from quant_algo_strategy.backtesting import Backtester
from quant_algo_strategy.subscription import PlotObserver, ConsoleObserver
from quant_algo_strategy.strategies import MovingAverageStrategy


def main():
    # Define the asset and date range
    asset = "AAPL"  # Apple stock
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 year of data

    # Load data
    print(f"Loading data for {asset} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    data_loader = YFinanceDataLoader(asset, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    data = data_loader.load_data()

    print(f"Data loaded. Shape: {data.shape}")
    print(data.head())

    # Create strategies with different parameters
    ma_strategy_20_50 = MovingAverageStrategy(data, short_window=20, long_window=50)
    ma_strategy_10_30 = MovingAverageStrategy(data, short_window=10, long_window=30)

    # Create backtester and attach observers
    backtester = Backtester()
    console_observer = ConsoleObserver()
    plot_observer = PlotObserver()

    backtester.attach(console_observer)
    backtester.attach(plot_observer)

    # Run backtests
    print("\nRunning backtest for MA(20, 50)...")
    backtester.run_backtest(ma_strategy_20_50, "MA(20, 50)")

    print("\nRunning backtest for MA(10, 30)...")
    backtester.run_backtest(ma_strategy_10_30, "MA(10, 30)")

    # Compare strategies
    print("\nComparing strategies...")
    backtester.compare_strategies()


if __name__ == "__main__":
    main()
