import streamlit as st
from datetime import datetime, timezone
from dukascopy_util import fetch_stock_indices_data
from analysisapp import dumb_buy_sell_strategy, moving_average_crossover_strategy, projection_pattern_strategy
from charting import generate_candlestick_chart, analyze_strategy_results # Import the separated functions

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
instrument_list = ["EUR/USD", "E_XJO-ASX", "E_NQ-100"]
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
strategy_params = {}
if selected_strategy_name == "Projection Pattern Strategy":
    strategy_params['pattern_len'] = st.slider("Pattern Length", min_value=1, max_value=8, value=4, step=1)
    strategy_params['proj_len'] = st.slider("Projection Length (future periods)", min_value=1, max_value=20, value=10, step=1)
    strategy_params['pattern_offset'] = st.slider("Pattern Start Offset (bars back)", min_value=1, max_value=10, value=1, step=1)
    strategy_params['max_matches'] = st.slider("Max Historical Matches", min_value=1, max_value=20, value=10, step=1)
    strategy_params['buy_threshold'] = st.number_input("Buy Signal Threshold (%)", min_value=0.0, value=2.0, step=0.1)
    strategy_params['sell_threshold'] = st.number_input("Sell Signal Threshold (%)", min_value=0.0, value=2.0, step=0.1)
    strategy_params['cooldown'] = st.slider("Signal Cooldown (bars)", min_value=1, max_value=20, value=5)
    strategy_params['min_bars'] = st.slider("Minimum Bars Before Signal Calculation", min_value=50, max_value=500, value=100)


# Fetch Button
if st.button("Fetch & Analyze"):
    try:
        st.write("🔹 Fetching Data...")
        df = fetch_stock_indices_data(
            instrument, offer_side, interval_options[interval], limit, time_direction
        )

        if not df.empty:
            st.success("✅ Data Fetched Successfully!")

            # Display simulation date range and starting capital
            st.subheader("Simulation Period and Initial Capital")
            st.write(f"📅 **Simulation Start Date (Data Earliest Date):** {df.index[0].strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"💰 **Starting Capital:** $10,000.00")
            st.write(f"📅 **Simulation End Date (Data Latest Date):** {df.index[-1].strftime('%Y-%m-%d %H:%M:%S')}")


            # Run selected strategy and get both results DataFrame and trade_log
            results, trade_log = selected_strategy(df, **strategy_params)

            # --- Analyze Results and Get Data for Tables/Summary ---
            summary_metrics, trade_df_for_display = analyze_strategy_results(results, trade_log)

            # Display Ending Capital after the summary metrics are calculated
            st.write(f"📈 **Ending Capital:** ${summary_metrics['Ending Capital']:,.2f}")


            # --- Display Chart ---
            chart_fig = generate_candlestick_chart(df, results) # Use the original df and results for chart
            st.plotly_chart(chart_fig, use_container_width=True)

            # --- Display Simple Trade Table ---
            st.subheader("Detailed Trade Log")
            if not trade_df_for_display.empty:
                st.dataframe(trade_df_for_display, height=300)
            else:
                st.write("No trades were executed by the strategy.")

            # --- Display Summary Section ---
            st.subheader("📊 Strategy Results Summary")
            st.write(f"**Starting Capital:** ${summary_metrics['Starting Capital']:,.2f}") # This will always be 10000 based on analysis_strategy_results
            st.write(f"**Max Drawdown:** {summary_metrics['Max Drawdown (%)']:,.2f}%")
            st.write(f"**Profitable Trades:** {summary_metrics['Profitable Trades (%)']:,.2f}% ({summary_metrics['Profitable Trades Count']}/{summary_metrics['Total Trades Count']})")


        else:
            st.error("❌ No data received.")
    except Exception as e:
        st.error(f"❌ Error: {e}")