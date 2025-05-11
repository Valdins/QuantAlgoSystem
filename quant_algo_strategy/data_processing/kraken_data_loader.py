
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
