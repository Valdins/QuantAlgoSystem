from abc import ABC, abstractmethod
from typing import Dict, Any


class Observer(ABC):
    """
    Observer interface for the Observer design pattern.
    """

    @abstractmethod
    def update(self, data: Dict[str, Any]) -> None:
        """
        Update method called by the subject when there's a change.

        Args:
            data: Data passed from the subject to the observer
        """
        pass


class ConsoleObserver(Observer):
    """
    Observer that prints backtest results to the console.
    """

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update method called by the subject when there's a change.

        Args:
            data: Data passed from the subject to the observer
        """
        if 'result' in data:
            result = data['result']
            result.print_metrics()


class PlotObserver(Observer):
    """
    Observer that plots backtest results.
    """

    def update(self, data: Dict[str, Any]) -> None:
        """
        Update method called by the subject when there's a change.

        Args:
            data: Data passed from the subject to the observer
        """
        #if 'result' in data and isinstance(data['result'], BacktestResult):
        if 'result' in data:
            result = data['result']
            result.plot_performance()