import streamlit as st
from datetime import datetime, timezone
from dukascopy_util import fetch_stock_indices_data
from analysisapp import dumb_buy_sell_strategy, moving_average_crossover_strategy, projection_pattern_strategy
from charting import display_chart_and_table

# Streamlit UI Setup
st.title("📊 Dukascopy JSONP Data Fetcher & Strategy Analyzer")

# Display Current UTC Time
current_utc = datetime.now(timezone.utc)
st.write(f"⏰ **Current UTC Time:** {current_utc.strftime('%Y-%m-%d %H:%M:%S')}")

# Intervals
interval_options = {
    "15 Minute": "15MIN",
    "1 Hour": "1HOUR",
    "1 Day": "1DAY"
}

# Inputs
instrument_list = ["EUR/USD", "E_XJO-ASX", "E_NQ-10"]
instrument = st.selectbox("Instrument", instrument_list, index=0)
offer_side = st.selectbox("Offer Side", ["B", "A"], index=0)
interval = st.selectbox("Interval", list(interval_options.keys()), index=0)
limit = st.number_input("Limit", min_value=1, value=100)
time_direction = st.selectbox("Time Direction", ["P", "N"], index=0)

# Strategy Selection
strategy_options = {
    "Dumb Buy/Sell": dumb_buy_sell_strategy,
    "Moving Average Crossover": moving_average_crossover_strategy,
    "Projection Pattern Strategy": projection_pattern_strategy
}

selected_strategy_name = st.selectbox("Select Strategy", list(strategy_options.keys()))
selected_strategy = strategy_options[selected_strategy_name]

# Parameters for Projection Pattern Strategy
if selected_strategy_name == "Projection Pattern Strategy":
    pattern_len = st.slider("Pattern Length", min_value=1, max_value=8, value=4, step=1)
    proj_len = st.slider("Projection Length (future periods)", min_value=1, max_value=20, value=10, step=1)
    pattern_offset = st.slider("Pattern Start Offset (bars back)", min_value=1, max_value=10, value=1, step=1)
    max_matches = st.slider("Max Historical Matches", min_value=1, max_value=20, value=10, step=1)
    buy_threshold = st.number_input("Buy Signal Threshold (%)", min_value=0.0, value=2.0, step=0.1)
    sell_threshold = st.number_input("Sell Signal Threshold (%)", min_value=0.0, value=2.0, step=0.1)
    cooldown = st.slider("Signal Cooldown (bars)", min_value=1, max_value=20, value=5)
    min_bars = st.slider("Minimum Bars Before Signal Calculation", min_value=50, max_value=500, value=100)

# Fetch Button
if st.button("Fetch & Analyze"):
    try:
        st.write("🔹 Fetching Data...")
        df = fetch_stock_indices_data(
            instrument, offer_side, interval_options[interval], limit, time_direction
        )

        if not df.empty:
            st.success("✅ Data Fetched Successfully!")
            st.write(f"📅 First Date: {df.index[0]}, Last Date: {df.index[-1]}")

            # Run selected strategy
            if selected_strategy_name == "Projection Pattern Strategy":
                results = selected_strategy(
                    df,
                    pattern_len=pattern_len,
                    proj_len=proj_len,
                    pattern_offset=pattern_offset,
                    max_matches=max_matches,
                    buy_threshold=buy_threshold,
                    sell_threshold=sell_threshold,
                    cooldown=cooldown,
                    min_bars=min_bars
                )
            else:
                results = selected_strategy(df)

            display_chart_and_table(df, results)
        else:
            st.error("❌ No data received.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
