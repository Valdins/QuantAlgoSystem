from kraken.spot import SpotWSClient

class KrakenDataClient(SpotWSClient):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url

    async def on_message(self, message: dict) -> None:
        """Receives the websocket messages"""
        if message.get("method") == "pong" or message.get("channel") == "heartbeat":
            return

        print(message)

        """
        {
            'channel': 'ticker',
            'type': 'snapshot',
            'data': [
                {
                    'symbol': 'BTC/USD',
                    'bid': 104170.7,
                    'bid_qty': 5.47575141,
                    'ask': 104170.8,
                    'ask_qty': 0.17344941,
                    'last': 104170.8,
                    'volume': 900.90713487,
                    'vwap': 104149.5,
                    'low': 103023.9,
                    'high': 104943.7,
                    'change': 666.8,
                    'change_pct': 0.64
                }
            ]
        }
        """
