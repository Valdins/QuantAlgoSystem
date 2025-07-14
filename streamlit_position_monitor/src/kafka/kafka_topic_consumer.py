import json

from kafka import KafkaConsumer
import streamlit as st

class KafkaTopicConsumer:
    def __init__(self, topic_name: str, server: str):
        self.kafka_consumer = KafkaConsumer(
        topic_name,
            bootstrap_servers=[server]
        )

    def start_to_process_market_data_messages(self):
        for message in self.kafka_consumer:
            msg_dict = json.loads(message.value.decode("utf-8"))
            #print(msg_dict)
            st.session_state["market_data_message_queue"].put(msg_dict)
            print(f"Market Data Queue Size: {st.session_state['market_data_message_queue'].qsize()}")

    def start_to_process_positions_messages(self):
        for message in self.kafka_consumer:
            msg_dict = json.loads(message.value.decode("utf-8"))
            #print(msg_dict)
            st.session_state["positions_message_queue"].put(msg_dict)
            print(f"Positions Queue Size: {st.session_state['positions_message_queue'].qsize()}")