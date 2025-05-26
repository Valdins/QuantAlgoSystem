import asyncio
from pathlib import Path

import pandas as pd

from quant_algo_strategy.backtesting.backtester_helper import BacktesterHelper
from quant_algo_strategy.configs import ConfigLoader


async def main():
    config = ConfigLoader("config.json").load_config()

    file_path = str(Path(__file__).parent.parent / "data" / "btcusd_1-min_data.csv")

    raw_btc_historical_data_df = pd.read_csv(file_path)

    btc_historical_data_df = BacktesterHelper.transform_kaggle_btc_data(raw_btc_historical_data_df)

    for index, row in btc_historical_data_df.iterrows():
        print(row)
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())