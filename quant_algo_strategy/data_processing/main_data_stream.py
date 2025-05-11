import asyncio

from quant_algo_strategy.configs import ConfigLoader
from quant_algo_strategy.data_processing import KrakenDataClient


async def main():
    config = ConfigLoader("config.json").load_config()

    krakenDataClient = KrakenDataClient(config['kraken']['api']['ws_endpoint'])

    await krakenDataClient.start()

    await krakenDataClient.subscribe(
        params={"channel": "ticker", "symbol": ["BTC/USD"]},
    )

    #await krakenDataClient.subscribe(params={"channel": "trade", "symbol": ["BTC/USD"]})

    await asyncio.sleep(3)

    await krakenDataClient.unsubscribe(
        params={"channel": "ticker", "symbol": ["BTC/USD"]},
    )

    await krakenDataClient.close()

if __name__ == "__main__":
    asyncio.run(main())
