import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone
from dukascopy_util import fetch_stock_indices_data

# Streamlit UI
st.title("📊 Dukascopy JSONP Data Fetcher & Plotter")

# Display Current UTC Time
current_utc = datetime.now(timezone.utc)
st.write(f"⏰ **Current UTC Time:** {current_utc.strftime('%Y-%m-%d %H:%M:%S')}")

# Available Intervals
interval_options = {
    "Tick": "TICK",
    "1 Second": "1SEC",
    "10 Second": "10SEC",
    "30 Second": "30SEC",
    "1 Minute": "1MIN",
    "5 Minute": "5MIN",
    "10 Minute": "10MIN",
    "15 Minute": "15MIN",
    "30 Minute": "30MIN",
    "1 Hour": "1H",
    "4 Hour": "4H",
    "1 Day": "1D",
    "1 Week": "1W",
    "1 Month": "1M"
}

instrument = st.text_input("Instrument (e.g., EUR/USD)", "EUR/USD")
offer_side = st.selectbox("Offer Side", ["B", "A"], index=0)  # Default: B
interval = st.selectbox("Interval", list(interval_options.keys()), index=7)  # Default: 15 Minute
limit = st.number_input("Limit", min_value=1, value=10)  # Default: 10
time_direction = st.selectbox("Time Direction", ["P", "N"], index=0)  # Default: P

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        st.write("🔹 Sending Request...")
        df = fetch_stock_indices_data(instrument, offer_side, interval_options[interval], limit, time_direction)

        if not df.empty:
            st.write("✅ Successfully Extracted Data!")

            # Debugging Info
            st.write(f"📅 **First Date in Data:** {df.index[0]}")
            st.write(f"📅 **Last Date in Data:** {df.index[-1]}")
            st.write(f"📊 **Total Timestamp Points Extracted:** {len(df)}")

            # Display Data
            st.write("🔹 Displaying first 5 rows of data:")
            st.dataframe(df.head())

            # Plot Candlestick Chart with Plotly
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price",
            )])

            fig.update_layout(title=f"Candlestick Chart for {instrument}", xaxis_title="Timestamp", yaxis_title="Price")
            st.plotly_chart(fig)

        else:
            st.error("❌ Failed to extract JSON data.")

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
