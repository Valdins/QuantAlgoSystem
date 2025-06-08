# Quantitative Trading System

A Python-based quantitative trading system for backtesting trading strategies using object-oriented programming and design patterns.

## Overview

This project implements a flexible and extensible framework for backtesting trading strategies. It uses object-oriented programming principles and design patterns to create a modular and maintainable codebase.

## Architecture

The system is built with the following components:

1. **Data Loading**: Abstract data loader interface with concrete implementations for different data sources.
2. **Strategy**: Abstract strategy interface with concrete implementations for different trading strategies.
3. **Backtester**: A backtester that runs strategies and collects performance metrics.
4. **Observer Pattern**: Implementation of the Observer pattern to handle and visualize backtest results.

## Design Patterns

The system uses the following design patterns:

1. **Strategy Pattern**: The `Strategy` abstract class defines an interface for all trading strategies. Concrete strategies like `MovingAverageStrategy` implement this interface.
2. **Observer Pattern**: The `Backtester` acts as a subject that notifies observers (like `ConsoleObserver` and `PlotObserver`) when backtest results are available.
3. **Template Method Pattern**: The `Strategy` class defines a template for strategies, with concrete implementations providing specific behavior.

## Components

### Data Loading

- `DataLoader`: Abstract base class for data loaders
- `YFinanceDataLoader`: Concrete implementation that loads data from Yahoo Finance

### Strategies

- `Strategy`: Abstract base class for all trading strategies
- `MovingAverageStrategy`: Implementation of a moving average crossover strategy

### Backtesting

- `Backtester`: Class for running backtests on strategies
- `BacktestResult`: Class for storing and analyzing backtest results

### Observers

- `Observer`: Interface for observers
- `Subject`: Base class for subjects in the Observer pattern
- `ConsoleObserver`: Observer that prints results to the console
- `PlotObserver`: Observer that plots performance charts

## Usage

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the main script:
   ```
   python main.py
   ```

3. To implement a new strategy:
   - Create a new class that inherits from `Strategy`
   - Implement the `generate_signals` and `backtest` methods

## Example

```python
# Load data
data_loader = YFinanceDataLoader("AAPL", "2022-01-01", "2023-01-01")
data = data_loader.load_data()

# Create strategy
strategy = MovingAverageStrategy(data, short_window=20, long_window=50)

# Create backtester and observers
backtester = Backtester()
backtester.attach(ConsoleObserver())
backtester.attach(PlotObserver())

# Run backtest
backtester.run_backtest(strategy, "MA(20, 50)")
```

## Future Enhancements

1. Add more strategy implementations (RSI, MACD, etc.)
2. Implement portfolio management and position sizing
3. Add risk management features
4. Implement more sophisticated performance metrics
5. Add support for more data sources