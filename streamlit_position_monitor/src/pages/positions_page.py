import streamlit as st


def positions_page():
    st.set_page_config(
        page_title="Live Positions Monitor",
        page_icon="💷",
    )

    st.title("Live Positions Monitor 💷")

    data_manager = st.session_state['positions_data_manager']

    # Create static layout elements
    st.subheader("Capital", divider="red")
    capital_cols = st.columns(4)

    st.subheader("Positions", divider="orange")
    positions_cols = st.columns(4)

    # Create placeholders in their respective columns
    metrics_containers = {
        "Initial Capital": capital_cols[0].empty(),
        "Current Capital": capital_cols[1].empty(),
        "Total Return %": capital_cols[2].empty(),
        "Total Profit": capital_cols[3].empty(),
        "Open Positions": positions_cols[0].empty(),
        "Total Positions": positions_cols[1].empty(),
        "Winning Positions": positions_cols[2].empty(),
        "Win Rate %": positions_cols[3].empty()
    }

    while True:
        while not st.session_state["positions_message_queue"].empty():
            message = st.session_state["positions_message_queue"].get()
            data = data_manager.process_latest_positions_data(message)

            # Update all metrics
            metrics_containers["Initial Capital"].metric(
                label="Initial Capital",
                value=f"{data['initial_capital']} £"
            )
            metrics_containers["Current Capital"].metric(
                label="Current Capital",
                value=f"{round(data['current_capital'], 2)} £",
                delta=f"{round(data['current_capital'] - data['initial_capital'], 2)} £"
            )
            metrics_containers["Total Return %"].metric(
                label="Total Return %",
                value=round(data["total_return_pct"], 2)
            )
            metrics_containers["Total Profit"].metric(
                label="Total Profit",
                value=f"{round(data['total_profit'], 2)} £"
            )
            metrics_containers["Open Positions"].metric(
                label="Open Positions",
                value=data["open_positions"]
            )
            metrics_containers["Total Positions"].metric(
                label="Total Positions",
                value=data["total_positions"]
            )
            metrics_containers["Winning Positions"].metric(
                label="Winning Positions",
                value=data["winning_positions"]
            )
            metrics_containers["Win Rate %"].metric(
                label="Win Rate %",
                value=round(data["win_rate_pct"], 2)
            )