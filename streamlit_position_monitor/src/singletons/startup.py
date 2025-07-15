import json
import os
import queue
import threading

import pandas as pd
import streamlit as st
from streamlit.runtime.scriptrunner_utils.script_run_context import add_script_run_ctx

from ..kafka.kafka_topic_consumer import KafkaTopicConsumer
from ..data_managers.data_manager import MarketDataManager, PositionsDataManager


def startup():
    if "market_data_message_queue" not in st.session_state:
        st.session_state["market_data_message_queue"] = queue.Queue()

    if "positions_message_queue" not in st.session_state:
        st.session_state["positions_message_queue"] = queue.Queue()

    if "chart_data" not in st.session_state:
        st.session_state["chart_data"] = pd.DataFrame(columns=["timestamp", "close"])

    if 'config' not in st.session_state:
        print("Load Config")
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
        with open(config_path, 'r') as f:
            st.session_state['config'] = json.load(f)

    if 'market_data_kafka_thread' not in st.session_state:
        print("Starting Market Data Kafka connection...")

        market_data_kafka_topic_consumer = KafkaTopicConsumer(
            topic_name=st.session_state['config']['kafka']['topics']['market_data'],
            server=st.session_state['config']['kafka']['server']
        )
        print("Add Market Data Kafka thread")
        market_data_kafka_thread = threading.Thread(target=market_data_kafka_topic_consumer.start_to_process_market_data_messages, daemon=True)
        add_script_run_ctx(market_data_kafka_thread)
        market_data_kafka_thread.start()
        st.session_state['market_data_kafka_thread'] = market_data_kafka_thread

    if 'positions_kafka_thread' not in st.session_state:
        print("Starting Positions Kafka connection...")

        positions_kafka_topic_consumer = KafkaTopicConsumer(
            topic_name=st.session_state['config']['kafka']['topics']['positions_data'],
            server=st.session_state['config']['kafka']['server']
        )
        print("Add Positions Kafka thread")
        positions_kafka_thread = threading.Thread(target=positions_kafka_topic_consumer.start_to_process_positions_messages, daemon=True)
        add_script_run_ctx(positions_kafka_thread)
        positions_kafka_thread.start()
        st.session_state['positions_kafka_thread'] = positions_kafka_thread

    if 'market_data_data_manager' not in st.session_state:
        print("Set DataManager")
        st.session_state['market_data_data_manager'] = MarketDataManager()

    if 'positions_data_manager' not in st.session_state:
        print("Set DataManager")
        st.session_state['positions_data_manager'] = PositionsDataManager()