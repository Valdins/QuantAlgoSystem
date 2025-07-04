import logging
from datetime import datetime
from typing import List, Callable, Optional, Dict

from .exit_condition import ExitCondition
from .position import Position
from quant_algo_strategy.enums import (
    PositionType,
    PositionStatus,
    Signal
)


class PositionManager:
    """
        Position Manager with flexible exit conditions.
    """

    def __init__(self, symbol: str, initial_capital: float = 10000):
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: List[Position] = []
        self.closed_positions: List[Position] = []
        self.exit_conditions: List[ExitCondition] = []
        self.max_positions = 5  # Maximum concurrent positions
        self.risk_per_trade = 0.05  # 5% risk per trade

        # Setup default exit conditions
        self._setup_default_exit_conditions()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _setup_default_exit_conditions(self):
        """Setup default exit conditions."""

        # Stop Loss condition
        def stop_loss_condition(position: Position, current_price: float) -> bool:
            if position.stop_loss is None:
                return False

            if position.position_type == PositionType.LONG:
                return current_price <= position.stop_loss
            else:  # SHORT
                return current_price >= position.stop_loss

        # Take Profit condition
        def take_profit_condition(position: Position, current_price: float) -> bool:
            if position.take_profit is None:
                return False

            if position.position_type == PositionType.LONG:
                return current_price >= position.take_profit
            else:  # SHORT
                return current_price <= position.take_profit

        # Add conditions with priorities
        self.add_exit_condition("stop_loss", stop_loss_condition, priority=10)
        self.add_exit_condition("take_profit", take_profit_condition, priority=9)


    def add_exit_condition(self, name: str, condition_func: Callable, priority: int = 5):
        """Add custom exit condition."""
        condition = ExitCondition(name, condition_func, priority)
        self.exit_conditions.append(condition)
        # Sort by priority (highest first)
        self.exit_conditions.sort(key=lambda x: x.priority, reverse=True)


    def calculate_position_size(self, entry_price: float, stop_loss: float = None) -> float:
        """Calculate position size based on risk management."""
        if stop_loss is None:
            # Default 2% stop loss
            stop_loss = entry_price * 0.98

        risk_amount = self.capital * self.risk_per_trade
        price_risk = abs(entry_price - stop_loss)

        if price_risk > 0:
            position_size = risk_amount / price_risk
        else:
            position_size = self.capital * 0.1 / entry_price  # Fallback to 10% of capital

        return min(position_size, self.capital * 0.2 / entry_price)  # Max 20% of capital per trade


    def open_position(self, signal: Signal, current_price: float,
                      current_time: datetime, strategy_id: str = "default",
                      stop_loss_pct: float = 2.0, take_profit_pct: float = 6.0) -> Optional[Position]:
        """
        Open a new position with automatic stop loss and take profit.

        Args:
            signal: BUY or SELL signal
            current_price: Current market price
            current_time: Current timestamp
            strategy_id: Strategy identifier
            stop_loss_pct: Stop loss percentage (default 2%)
            take_profit_pct: Take profit percentage (default 6%)
        """

        # Check if we can open more positions
        if len(self.positions) >= self.max_positions:
            self.logger.warning(f"Maximum positions ({self.max_positions}) reached. Cannot open new position.")
            return None

        # Determine position type
        if signal == Signal.BUY:
            position_type = PositionType.LONG
            stop_loss = current_price * (1 - stop_loss_pct / 100)
            take_profit = current_price * (1 + take_profit_pct / 100)
        elif signal == Signal.SELL:
            position_type = PositionType.SHORT
            stop_loss = current_price * (1 + stop_loss_pct / 100)
            take_profit = current_price * (1 - take_profit_pct / 100)
        else:
            return None

        # Calculate position size
        size = self.calculate_position_size(current_price, stop_loss)

        # Create and add position
        position = Position(
            entry_price=current_price,
            entry_time=current_time,
            position_type=position_type,
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy_id=strategy_id
        )

        self.positions.append(position)

        self.logger.info(f"Opened {position_type.value} position: "
                         f"Price={current_price:.2f}, Size={size:.4f}, "
                         f"SL={stop_loss:.2f}, TP={take_profit:.2f}")

        return position


    def check_exit_conditions(self, current_price: float, current_time: datetime) -> List[Position]:
        """
        Check all positions against exit conditions.

        Returns:
            List of positions that were closed
        """
        closed_positions = []

        for position in self.positions[:]:  # Create copy to iterate
            for condition in self.exit_conditions:
                if condition.condition_func(position, current_price):
                    # Close position
                    self.close_position(position, current_price, current_time, condition.name)
                    closed_positions.append(position)
                    break  # Stop checking other conditions for this position

        return closed_positions


    def close_position(self, position: Position, exit_price: float,
                       exit_time: datetime, reason: str = "manual"):
        """Close a specific position."""
        position.close(exit_price, exit_time, reason)

        # Update capital
        profit = position.calculate_profit_absolute(exit_price)
        self.capital += profit

        # Move to closed positions
        if position in self.positions:
            self.positions.remove(position)
        self.closed_positions.append(position)

        self.logger.info(f"Closed {position.position_type.value} position: "
                         f"Entry={position.entry_price:.2f}, Exit={exit_price:.2f}, "
                         f"Profit={profit:.2f} ({position.calculate_profit_pct(exit_price):.2f}%), "
                         f"Reason={reason}")


    def close_all_positions(self, current_price: float, current_time: datetime, reason: str = "manual"):
        """Close all open positions."""
        closed_positions = []
        for position in self.positions[:]:
            self.close_position(position, current_price, current_time, reason)
            closed_positions.append(position)
        return closed_positions


    def process_signal(self, signal: Signal, current_price: float,
                       current_time: datetime, strategy_name: str):
        """
        Process trading signal and manage positions.
        """
        # First check exit conditions for existing positions
        self.check_exit_conditions(current_price, current_time)

        # Then process new signal
        if signal in [Signal.BUY, Signal.SELL]:
            # Check if we have conflicting positions
            conflicting_positions = [
                p for p in self.positions
                if ((signal == Signal.BUY and p.position_type == PositionType.SHORT) or
                    (signal == Signal.SELL and p.position_type == PositionType.LONG))
                   and p.strategy_id == strategy_name
            ]

            # Close conflicting positions
            for position in conflicting_positions:
                self.close_position(position, current_price, current_time, "signal_reversal")

            # Open new position
            self.open_position(signal, current_price, current_time, strategy_name)


    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary."""
        total_positions = len(self.closed_positions)
        winning_positions = len([p for p in self.closed_positions if p.calculate_profit_pct() > 0])

        total_profit = sum(p.calculate_profit_absolute() for p in self.closed_positions)
        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100

        win_rate = (winning_positions / total_positions * 100) if total_positions > 0 else 0

        # Current open positions value
        unrealized_pnl = sum(p.calculate_profit_absolute() for p in self.positions) if self.positions else 0

        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.capital,
            'total_return_pct': total_return,
            'total_profit': total_profit,
            'unrealized_pnl': unrealized_pnl,
            'open_positions': len(self.positions),
            'total_positions': total_positions,
            'winning_positions': winning_positions,
            'win_rate_pct': win_rate,
            'positions_by_strategy': self._get_positions_by_strategy()
        }


    def _get_positions_by_strategy(self) -> Dict:
        """Get position breakdown by strategy."""
        strategy_stats = {}
        all_positions = self.positions + self.closed_positions

        for pos in all_positions:
            if pos.strategy_id not in strategy_stats:
                strategy_stats[pos.strategy_id] = {
                    'total': 0, 'open': 0, 'closed': 0, 'winning': 0
                }

            stats = strategy_stats[pos.strategy_id]
            stats['total'] += 1

            if pos.status == PositionStatus.OPEN:
                stats['open'] += 1
            else:
                stats['closed'] += 1
                if pos.calculate_profit_pct() > 0:
                    stats['winning'] += 1

        return strategy_stats