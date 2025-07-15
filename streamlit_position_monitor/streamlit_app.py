import streamlit as st

from src.singletons.startup import startup
from src.pages.market_data_page import market_data_page
from src.pages.positions_page import positions_page

def home_page():
   startup()

   st.set_page_config(
       page_title="Algo Trading System UI",
       page_icon="🏛️",
   )

   st.sidebar.title("Algo Trading System UI")

   st.title("Welcome to the Algo Trading System Dashboard 🏛️")

   # Add standalone badges
   st.badge("New")
   st.badge("Success", icon=":material/check:", color="green")

   # Overview section with colored text
   st.markdown("""
       ## :blue[Overview]

       This dashboard provides :green[real-time monitoring] and :orange[visualization tools] for algorithmic trading strategies. 
       Track your trading performance and market movements all in one place.
   """)

   # Add a "New" badge for the features section
   st.markdown("## Features :violet-badge[:material/star: Premium]")

   # Market Data View section with highlighting and emojis
   st.markdown("""
       ### 📈 :red[Live Market Data View]

       - :green[Real-time] price charts for monitored assets
       - :blue-background[Visual trend analysis] with dynamic scaling
       - :orange[Instant market updates] for informed decision making
   """)

   # Positions Monitor section with colored text and badges
   st.markdown("""
       ### 💷 :blue[Live Positions Monitor] :green-badge[⚠️ Live]

       - Track :violet[open] and :gray[closed] trading positions
       - Monitor key performance metrics:
           - Initial and current capital
           - Total returns and profits
           - Win rate and position statistics
   """)

   # Getting Started section with rainbow text
   st.markdown("""
       ## :rainbow[Getting Started]

       Use the navigation menu to switch between views. Data is updated in real-time from 
       connected trading systems and market data feeds.
   """)

   # Add a bouquet of emojis
   st.markdown("### Trading Instruments Available: :chart_with_upwards_trend::currency_exchange::moneybag::gem::chart_with_downwards_trend:")

   # Add a multi-line text with proper line breaks
   st.markdown("""
       ---

       *Developed for algorithmic trading strategy monitoring and evaluation*  
       *Version 1.0.0*  
       *© 2023 Algo Trading Systems*
   """)

pg = st.navigation([
   st.Page(home_page, title="Home", icon="🏛️"),
   st.Page(positions_page, title="Live Positions Monitor", icon="💷"),
   st.Page(market_data_page, title="Live Market Data View", icon="📈"),
])

pg.run()
