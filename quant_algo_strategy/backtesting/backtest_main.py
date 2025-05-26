from quant_algo_strategy.positions import PositionsManager
from quant_algo_strategy.strategies import MovingAverageStrategy
from quant_algo_strategy.configs import ConfigLoader

def main():
    config = ConfigLoader("config.json").load_config()

    position_manager = PositionsManager()

    ma_strategy_20_50 = MovingAverageStrategy(data, short_window=20, long_window=50)

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

    print("\nRunning backtest for Advanced MA Strategy with TP/SL 4%...")
    adv_result = backtester.run_backtest(adv_ma_strategy, "Advanced MA with TP/SL 4%")

    # Plot the advanced strategy's moving averages
    print("\nPlotting Advanced MA Strategy's moving averages...")
    adv_ma_strategy.plot_ma()

    # Compare strategies
    print("\nComparing strategies...")
    backtester.compare_strategies()


if __name__ == "__main__":
    main()
