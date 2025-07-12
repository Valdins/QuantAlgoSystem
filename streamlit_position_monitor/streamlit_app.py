import streamlit as st
import pandas as pd

from src.singletons.startup import startup


startup()

st.title("Market and Positions Monitor")

market_data = st.session_state["message_queue"]

chart_data = pd.DataFrame(
   {
      "timestamp": market_data["timestamp"],
      "close": market_data["close"],
   }
)

st.line_chart(chart_data, x="timestamp", y="close")