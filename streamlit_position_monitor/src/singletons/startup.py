import json
import os

import streamlit as st

from ..kafka.kafka_topic_consumer import KafkaTopicConsumer
from ..data_managers.data_manager import DataManager


def startup():
    if "message_queue" not in st.session_state:
        st.session_state["message_queue"] = []

    if 'config' not in st.session_state:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')
        with open(config_path, 'r') as f:
            st.session_state['config'] = json.load(f)

    if 'data_manager' not in st.session_state:
        kafka_topic_consumer = KafkaTopicConsumer(topic_name=st.session_state['config']['kafka']['topic'], server=st.session_state['config']['kafka']['server'])
        kafka_topic_consumer.start_to_process_messages()
        st.session_state['kafka_topic_consumer'] = kafka_topic_consumer

    if 'data_manager' not in st.session_state:
        st.session_state['data_manager'] = DataManager()