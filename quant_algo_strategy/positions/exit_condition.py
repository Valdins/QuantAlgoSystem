from dataclasses import dataclass
from typing import Callable


@dataclass
class ExitCondition:
    """Defines conditions for closing positions."""
    name: str
    condition_func: Callable  # Function that takes (position, current_price, current_time) -> bool
    priority: int = 1  # Higher priority conditions are checked first