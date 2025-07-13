import os

import pandas as pd

from streamlit_position_monitor.src.data_managers.data_manager import DataManager
from streamlit_position_monitor.src.kafka.kafka_topic_consumer import KafkaTopicConsumer


def test_streamlit_app():
    message_queue = []

    kafka_topic_consumer = KafkaTopicConsumer(
        topic_name="marketdata.quotes",
        server="localhost:9092"
    )

    msg = next(kafka_topic_consumer.start_to_process_messages_test())

    message_queue.append(msg)

    data_manager = DataManager()

    if len(message_queue) > 0:
        data = data_manager.process_latest_data(message_queue.pop())
    else:
        data = data_manager.data


    chart_data = pd.DataFrame(
        {
            "timestamp": data.index,
            "close": data["close"],
        }
    )

if __name__ == "__main__":
    test_streamlit_app()