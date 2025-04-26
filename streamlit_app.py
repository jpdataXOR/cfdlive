import streamlit as st
from datetime import datetime, timezone
from dukascopy_util import fetch_stock_indices_data
from analysisapp import dumb_buy_sell_strategy, moving_average_crossover_strategy, projection_pattern_strategy
from charting import generate_candlestick_chart, analyze_strategy_results # Import the separated functions
import pandas as pd # Import pandas for DataFrame operations
import itertools # Import itertools for parameter combinations
import numpy as np # Import numpy for arange


# Streamlit UI Setup
st.title("📊 Dukascopy JSONP Data Fetcher & Strategy Analyzer")

# Display Current UTC Time
current_utc = datetime.now(timezone.utc)
st.write(f"⏰ **Current UTC Time:** {current_utc.strftime('%Y-%m-%d %H:%M:%S')}")

# Create tabs
tab1, tab2 = st.tabs(["📈 Strategy Analyzer", "🔬 Strategy Optimizer"])

# --- Strategy Analyzer Tab ---
with tab1:
    st.header("Strategy Backtesting and Analysis")

    # Intervals
    interval_options = {
        "15 Minute": "15MIN",
        "1 Hour": "1HOUR",
        "1 Day": "1DAY"
    }

    # Inputs
    instrument_list = ["EUR/USD", "E_XJO-ASX", "E_NQ-10"]
    instrument = st.selectbox("Instrument", instrument_list, index=0, key='analyzer_instrument') # Added unique key
    offer_side = st.selectbox("Offer Side", ["B", "A"], index=0, key='analyzer_offer_side') # Added unique key
    interval = st.selectbox("Interval", list(interval_options.keys()), index=0, key='analyzer_interval') # Added unique key
    limit = st.number_input("Limit", min_value=1, value=100, key='analyzer_limit') # Added unique key
    time_direction = st.selectbox("Time Direction", ["P", "N"], index=0, key='analyzer_time_direction') # Added unique key

    # Strategy Selection
    strategy_options = {
        "Dumb Buy/Sell": dumb_buy_sell_strategy,
        "Moving Average Crossover": moving_average_crossover_strategy,
        "Projection Pattern Strategy": projection_pattern_strategy
    }

    selected_strategy_name = st.selectbox("Select Strategy", list(strategy_options.keys()), key='analyzer_strategy') # Added unique key
    selected_strategy = strategy_options[selected_strategy_name]

    # Parameters for Projection Pattern Strategy
    strategy_params = {}
    if selected_strategy_name == "Projection Pattern Strategy":
        st.subheader("Projection Pattern Strategy Parameters")
        strategy_params['pattern_len'] = st.slider("Pattern Length", min_value=1, max_value=8, value=4, step=1, key='analyzer_pattern_len') # Added unique key
        strategy_params['proj_len'] = st.slider("Projection Length (future periods)", min_value=1, max_value=20, value=10, step=1, key='analyzer_proj_len') # Added unique key
        strategy_params['pattern_offset'] = st.slider("Pattern Start Offset (bars back)", min_value=1, max_value=10, value=1, step=1, key='analyzer_pattern_offset') # Added unique key
        strategy_params['max_matches'] = st.slider("Max Historical Matches", min_value=1, max_value=20, value=10, step=1, key='analyzer_max_matches') # Added unique key
        strategy_params['buy_threshold'] = st.number_input("Buy Signal Threshold (%)", min_value=0.0, value=2.0, step=0.1, key='analyzer_buy_threshold') # Added unique key
        strategy_params['sell_threshold'] = st.number_input("Sell Signal Threshold (%)", min_value=0.0, value=2.0, step=0.1, key='analyzer_sell_threshold') # Added unique key
        strategy_params['cooldown'] = st.slider("Signal Cooldown (bars)", min_value=1, max_value=20, value=5, key='analyzer_cooldown') # Added unique key
        strategy_params['min_bars'] = st.slider("Minimum Bars Before Signal Calculation", min_value=50, max_value=500, value=100, key='analyzer_min_bars') # Added unique key


    # Fetch Button for Analyzer
    if st.button("Fetch & Analyze", key='run_analyzer'): # Added unique key
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


# --- Strategy Optimizer Tab ---
with tab2:
    st.header("Projection Pattern Strategy Optimizer")
    st.write("Iterate through Buy and Sell Signal Thresholds to find the most profitable settings, while other parameters are set using sliders.")
    st.warning("Note: Optimizing over large parameter ranges can be computationally intensive and may cause the app to be slow or unresponsive.")

    # Inputs for Optimizer
    instrument_list_opt = ["EUR/USD", "E_XJO-ASX", "E_NQ-10"]
    instrument_opt = st.selectbox("Instrument", instrument_list_opt, index=0, key='optimizer_instrument') # Added unique key
    offer_side_opt = st.selectbox("Offer Side", ["B", "A"], index=0, key='optimizer_offer_side') # Added unique key
    interval_opt = st.selectbox("Interval", list(interval_options.keys()), index=0, key='optimizer_interval') # Added unique key
    limit_opt = st.number_input("Limit", min_value=1, value=200, key='optimizer_limit') # Added unique key - Increased limit for optimization

    st.subheader("Projection Pattern Strategy Parameters (Optimizer)")
    st.write("Set specific values for most parameters, and define ranges for Buy/Sell Thresholds.")

    # Define single value sliders for parameters not being ranged
    pattern_len_opt = st.slider("Pattern Length", min_value=1, max_value=8, value=4, step=1, key='opt_pattern_len')
    proj_len_opt = st.slider("Projection Length (future periods)", min_value=1, max_value=20, value=10, step=1, key='opt_proj_len')
    pattern_offset_opt = st.slider("Pattern Start Offset (bars back)", min_value=1, max_value=10, value=1, step=1, key='opt_pattern_offset')
    max_matches_opt = st.slider("Max Historical Matches", min_value=1, max_value=20, value=10, step=1, key='opt_max_matches')
    cooldown_opt = st.slider("Signal Cooldown (bars)", min_value=1, max_value=10, value=5, step=1, key='opt_cooldown')
    min_bars_opt = st.slider("Minimum Bars Before Signal Calculation", min_value=50, max_value=500, value=100, key='opt_min_bars')


    # Define ranges for parameters to optimize (Buy/Sell Thresholds)
    st.subheader("Optimization Ranges")
    buy_threshold_step = 0.01 # Define the step separately
    buy_threshold_range = st.slider("Buy Signal Threshold (%) Range", min_value=0.0, max_value=5.0, value=(0.1, 2.0), step=buy_threshold_step, key='opt_buy_threshold_range')
    sell_threshold_step = 0.01 # Define the step separately
    sell_threshold_range = st.slider("Sell Signal Threshold (%) Range", min_value=0.0, max_value=5.0, value=(0.1, 2.0), step=sell_threshold_step, key='opt_sell_threshold_range')


    # Generate parameter combinations - only for the ranges
    param_combinations = list(itertools.product(
        [pattern_len_opt], # Use single value from slider
        [proj_len_opt], # Use single value from slider
        [pattern_offset_opt], # Use single value from slider
        [max_matches_opt], # Use single value from slider
        np.arange(buy_threshold_range[0], buy_threshold_range[1] + buy_threshold_step, buy_threshold_step), # Use range for buy threshold
        np.arange(sell_threshold_range[0], sell_threshold_range[1] + sell_threshold_step, sell_threshold_step), # Use range for sell threshold
        [cooldown_opt], # Use single value from slider
        [min_bars_opt] # Use single value from slider
    ))

    # Convert float parameters to rounded values for display/keys if needed, but use raw for calculation
    # Adjusted rounding to match the potential step size for buy_threshold and sell_threshold
    param_combinations = [(p[0], p[1], p[2], p[3], round(p[4], 3), round(p[5], 3), p[6], p[7]) for p in param_combinations]


    st.write(f"Testing {len(param_combinations)} parameter combinations.")


    # Optimization Button
    if st.button("Run Optimization", key='run_optimizer'): # Added unique key
        if not param_combinations:
            st.warning("Please define valid parameter ranges.")
            st.stop()

        try:
            st.write("🔹 Fetching Data for Optimization...")
            df_opt = fetch_stock_indices_data(
                instrument_opt, offer_side_opt, interval_options[interval_opt], limit_opt, "P" # Always use "P" for optimization
            )

            if df_opt.empty:
                st.error("❌ No data received for optimization.")
                st.stop()

            st.success("✅ Data Fetched Successfully!")
            st.write("🔬 Running optimization...")

            best_profit = -float('inf')
            best_params = None
            optimization_results = []

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Iterate directly over itertools.product or the list
            for i, params in enumerate(param_combinations): # Iterating over the list generated upfront
                pattern_len, proj_len, pattern_offset, max_matches, buy_threshold, sell_threshold, cooldown, min_bars = params

                # Run the strategy with the current parameters
                current_params = {
                    'pattern_len': pattern_len,
                    'proj_len': proj_len,
                    'pattern_offset': pattern_offset,
                    'max_matches': max_matches,
                    'buy_threshold': buy_threshold,
                    'sell_threshold': sell_threshold,
                    'cooldown': cooldown,
                    'min_bars': min_bars
                }
                # Pass a copy of df_opt to ensure each strategy run is independent
                results_opt, trade_log_opt = projection_pattern_strategy(df_opt.copy(), **current_params)

                # Calculate profit for this run
                starting_capital_opt = 10000
                ending_capital_opt = results_opt['Equity'].iloc[-1] if not results_opt.empty and 'Equity' in results_opt.columns else starting_capital_opt
                current_profit = ending_capital_opt - starting_capital_opt

                optimization_results.append({
                    'Parameters': params,
                    'Ending Capital': ending_capital_opt,
                    'Profit': current_profit
                })

                # Check if this is the best profit found so far
                if current_profit > best_profit:
                    best_profit = current_profit
                    best_params = params

                # Update progress bar and status text
                progress = (i + 1) / len(param_combinations)
                progress_bar.progress(progress)
                status_text.text(f"Completed {i + 1}/{len(param_combinations)} combinations. Current best profit: ${best_profit:,.2f}")


            st.subheader("Optimization Results")

            if best_params:
                st.success(f"🏆 **Optimization Complete!**")
                st.write(f"**Best Parameters Found:**")
                st.write(f"- Pattern Length: {best_params[0]}")
                st.write(f"- Projection Length: {best_params[1]}")
                st.write(f"- Pattern Start Offset: {best_params[2]}")
                st.write(f"- Max Historical Matches: {best_params[3]}")
                st.write(f"- Buy Signal Threshold (%): {best_params[4]:,.3f}") # Adjusted formatting for display
                st.write(f"- Sell Signal Threshold (%): {best_params[5]:,.3f}") # Adjusted formatting for display
                st.write(f"- Signal Cooldown (bars): {best_params[6]}")
                st.write(f"- Minimum Bars: {best_params[7]}")
                st.write(f"**Maximum Profit:** ${best_profit:,.2f}")
                st.write(f"**Corresponding Ending Capital:** ${best_profit + 10000:,.2f}") # Assuming starting capital is 10000


            # Optionally display a table of all results (can be large)
            if st.checkbox("Show all optimization results"):
                 optimization_results_df = pd.DataFrame(optimization_results)
                 st.dataframe(optimization_results_df.sort_values(by='Profit', ascending=False))


        except Exception as e:
            st.error(f"❌ Error during optimization: {e}")


