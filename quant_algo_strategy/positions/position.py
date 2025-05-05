
class Position:
    """
    Class to represent a trading position.
    """

    def __init__(self, entry_price, entry_time, position_type, size=1.0):
        """
        Initialize a position.

        Args:
            entry_price (float): Entry price
            entry_time (datetime): Entry time
            position_type (str): 'long' or 'short'
            size (float): Position size
        """
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.position_type = position_type
        self.size = size
        self.exit_price = None
        self.exit_time = None
        self.status = 'open'

    def close(self, exit_price, exit_time):
        """
        Close the position.

        Args:
            exit_price (float): Exit price
            exit_time (datetime): Exit time
        """
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.status = 'closed'

    def calculate_profit(self, current_price=None):
        """
        Calculate the profit/loss of the position.

        Args:
            current_price (float, optional): Current price for open positions

        Returns:
            float: Profit/loss as a percentage
        """
        if self.status == 'closed':
            if self.position_type == 'long':
                return (self.exit_price - self.entry_price) / self.entry_price * 100
            else:  # short
                return (self.entry_price - self.exit_price) / self.entry_price * 100
        else:
            if current_price is None:
                return 0.0

            if self.position_type == 'long':
                return (current_price - self.entry_price) / self.entry_price * 100
            else:  # short
                return (self.entry_price - current_price) / self.entry_price * 100
