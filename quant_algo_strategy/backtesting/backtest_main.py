import pandas as pd

from quant_algo_strategy.data_processing.timeframe_manager import TimeframeManager
from quant_algo_strategy.data_processing.data_loader import KaggleDataLoader
from quant_algo_strategy.kafka.KafkaTopicProducer import KafkaTopicProducer
from quant_algo_strategy.positions.positions_manager import PositionManager
from quant_algo_strategy.strategies import MovingAverageStrategy
from quant_algo_strategy.backtesting import Backtester
from quant_algo_strategy.enums import Timeframe


def main():
    """
        Data Loading
    """
    data_loader = KaggleDataLoader()

    """
        Kafka Topic Producer
    """
    market_data_kafka_topic_producer = KafkaTopicProducer(server='localhost:9092', topic_name='marketdata.quotes')
    positions_kafka_topic_producer = KafkaTopicProducer(server='localhost:9092', topic_name='positions.quotes.v1')

    """
        Strategy
    """
    timeframe = Timeframe.MIN_15
    short_window = 10
    long_window = 20

    ma_strategy = MovingAverageStrategy(
        data_timeframe=timeframe,
        strategy_name='ma_strategy',
        short_window=short_window,
        long_window=long_window
    )

    """
        Positions Management
    """
    position_manager = PositionManager(
        kafka_topic_producer=positions_kafka_topic_producer,
        symbol='BTC/USD',
        initial_capital=1000
    )

    """
        Timeframe Manager
    """
    timeframe_manager = TimeframeManager()

    # ------------------ Main ------------------

    backtester = Backtester(
        data_loader=data_loader,
        strategy=ma_strategy,
        kafka_topic_producer=market_data_kafka_topic_producer
    )

    backtester.run_backtest(
        position_manager=position_manager,
        timeframe_manager=timeframe_manager
    )


if __name__ == "__main__":
    main()
