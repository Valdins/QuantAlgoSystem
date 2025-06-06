from datetime import datetime

from quant_algo_strategy.enums import PositionType, PositionStatus


class Position:
    """Enhanced Position class with more tracking capabilities."""

    def __init__(self, entry_price: float, entry_time: datetime,
                 position_type: PositionType, size: float = 1.0,
                 stop_loss: float = None, take_profit: float = None,
                 strategy_id: str = "default"):
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.position_type = position_type
        self.size = size
        self.stop_loss = stop_loss  # Absolute price level
        self.take_profit = take_profit  # Absolute price level
        self.strategy_id = strategy_id
        self.exit_price = None
        self.exit_time = None
        self.exit_reason = None
        self.status = PositionStatus.OPEN
        self.max_profit = 0.0
        self.max_loss = 0.0

    def close(self, exit_price: float, exit_time: datetime, reason: str = "manual"):
        """Close the position with reason tracking."""
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.exit_reason = reason
        self.status = PositionStatus.CLOSED

    def update_extremes(self, current_price: float):
        """Update max profit and loss tracking."""
        current_profit_pct = self.calculate_profit_pct(current_price)
        self.max_profit = max(self.max_profit, current_profit_pct)
        self.max_loss = min(self.max_loss, current_profit_pct)

    def calculate_profit_pct(self, current_price: float = None) -> float:
        """Calculate profit/loss as percentage."""
        if self.status == PositionStatus.CLOSED:
            price = self.exit_price
        else:
            price = current_price if current_price else self.entry_price

        if self.position_type == PositionType.LONG:
            return (price - self.entry_price) / self.entry_price * 100
        else:  # SHORT
            return (self.entry_price - price) / self.entry_price * 100

    def calculate_profit_absolute(self, current_price: float = None) -> float:
        """Calculate absolute profit/loss."""
        return self.calculate_profit_pct(current_price) * self.size * self.entry_price / 100