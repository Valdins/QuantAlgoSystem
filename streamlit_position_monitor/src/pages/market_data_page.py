import streamlit as st
import altair as alt
import pandas as pd

from ..singletons.startup import startup

startup()

st.title("Live Market Data View")

data_manager = st.session_state['data_manager']

# Create a placeholder for the chart
chart_placeholder = st.empty()

while True:
   while not st.session_state["market_data_message_queue"].empty():
      message = st.session_state["market_data_message_queue"].get()
      data = data_manager.process_latest_market_data(message)

      # Update the existing chart data
      new_data = pd.DataFrame({
         "timestamp": data.index,
         "close": data["close"],
      })
      st.session_state["chart_data"] = new_data

      # Calculate min/max values for y-axis padding
      y_min = st.session_state["chart_data"]["close"].min()
      y_max = st.session_state["chart_data"]["close"].max()
      y_padding = (y_max - y_min) * 0.1

      # Create Altair chart with custom y-axis range
      chart = alt.Chart(st.session_state["chart_data"]).mark_line().encode(
         x='timestamp:T',
         y=alt.Y('close:Q', scale=alt.Scale(
            domain=[y_min - y_padding, y_max + y_padding]
         ))
      ).properties(
         width=700,
         height=400
      )

      # Update the chart in place
      chart_placeholder.altair_chart(chart, use_container_width=True)