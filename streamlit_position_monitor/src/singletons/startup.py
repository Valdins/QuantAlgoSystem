import json
import os
import queue
import threading

import pandas as pd
import streamlit as st
from streamlit.runtime.scriptrunner_utils.script_run_context import add_script_run_ctx

from ..kafka.kafka_topic_consumer import KafkaTopicConsumer
from ..data_managers.data_manager import DataManager


def startup():
    if "message_queue" not in st.session_state:
        st.session_state["message_queue"] = queue.Queue()

    if "chart_data" not in st.session_state:
        st.session_state["chart_data"] = pd.DataFrame(columns=["timestamp", "close"])

    if 'config' not in st.session_state:
        print("Load Config")
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
        with open(config_path, 'r') as f:
            st.session_state['config'] = json.load(f)

    if 'kafka_thread' not in st.session_state:
        print("Starting Kafka connection...")

        kafka_topic_consumer = KafkaTopicConsumer(
            topic_name=st.session_state['config']['kafka']['topic'],
            server=st.session_state['config']['kafka']['server']
        )
        print("Add Kafka thread")
        kafka_thread = threading.Thread(target=kafka_topic_consumer.start_to_process_messages, daemon=True)
        add_script_run_ctx(kafka_thread)
        print("Kafka Start")
        kafka_thread.start()
        print("After Kafka thread")
        st.session_state['kafka_thread'] = kafka_thread

    if 'data_manager' not in st.session_state:
        print("Set DataManager")
        st.session_state['data_manager'] = DataManager()