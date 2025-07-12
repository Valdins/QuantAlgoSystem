import json

import pandas as pd
from kafka import KafkaProducer


class KafkaTopicProducer:
    def __init__(self, server: str, topic_name: str):
        self._topic_name = topic_name
        self._producer = KafkaProducer(
            bootstrap_servers=[server],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

    def send(self, message: dict):
        processed_message = {}
        for key, value in message.items():
            if isinstance(value, pd.Timestamp):
                processed_message[key] = value.isoformat()
            elif isinstance(value, pd.Series):
                processed_message[key] = value.to_dict()
            else:
                processed_message[key] = value

        self._producer.send(self._topic_name, processed_message)
        self._producer.flush()