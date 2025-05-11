import asyncio

from quant_algo_strategy.configs import ConfigLoader
from quant_algo_strategy.data_processing import KrakenDataClient


async def main():
    config = ConfigLoader("config.json").load_config()

    krakenDataClient = KrakenDataClient(config['kraken']['api']['ws_endpoint'])
    assets = config['kraken']['assets']

    await krakenDataClient.start()

    await krakenDataClient.subscribe(
        params={"channel": "ticker", "symbol": assets},
    )

    #await krakenDataClient.subscribe(params={"channel": "trade", "symbol": assets})

    await asyncio.sleep(3)

    await krakenDataClient.unsubscribe(
        params={"channel": "ticker", "symbol": assets},
    )

    await krakenDataClient.close()

if __name__ == "__main__":
    asyncio.run(main())
