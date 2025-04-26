import pandas as pd
import plotly.graph_objects as go
# import streamlit as st # Remove streamlit import for calculation only
import numpy as np

# Keep the chart generation function separate, as it requires streamlit
def generate_candlestick_chart(df: pd.DataFrame, df_signals: pd.DataFrame):
    fig = go.Figure()

    # Candlestick base
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Price"
    ))

    # Buy signals
    buy_signals = df_signals[df_signals['Signal'] == 'BUY'].copy()
    fig.add_trace(go.Scatter(
        x=buy_signals.index,
        y=buy_signals['BuyPrice'],
        mode='markers',
        marker=dict(color='green', symbol='triangle-up', size=10),
        name='Buy'
    ))

    # Sell signals
    sell_signals = df_signals[df_signals['Signal'] == 'SELL'].copy()
    fig.add_trace(go.Scatter(
        x=sell_signals.index,
        y=sell_signals['SellPrice'],
        mode='markers',
        marker=dict(color='red', symbol='triangle-down', size=10),
        name='Sell'
    ))

    # Layout
    fig.update_layout(
        title="💹 Strategy Chart with Signals",
        xaxis_title="Date",
        yaxis_title="Price",
        height=600
    )
    return fig # Return the figure instead of displaying it


def analyze_strategy_results(df_signals: pd.DataFrame, trade_log: list):
    """
    Analyzes strategy results and prepares data for display.
    Returns summary metrics and the trade table DataFrame.
    """
    # --- Simple Trade Table ---
    trade_df = pd.DataFrame() # Initialize empty DataFrame

    if trade_log:
        trade_df = pd.DataFrame(trade_log)
        trade_df.set_index('Date', inplace=True)
        # Ensure ascending order by index (Date)
        trade_df.sort_index(ascending=True, inplace=True)

        # Select and rename columns
        trade_df = trade_df[['Capital', 'Buy/sell', 'Invested in this trade']]


    # --- Summary Section ---
    starting_capital = 10000
    ending_capital = df_signals['Equity'].iloc[-1] if not df_signals.empty and 'Equity' in df_signals.columns else starting_capital

    # Calculate Max Drawdown Percentage
    max_drawdown_percentage = 0.0
    if 'Equity' in df_signals.columns and not df_signals.empty:
        # Calculate peak equity up to each point
        peak_equity = df_signals['Equity'].cummax()
        # Calculate drawdown at each point
        drawdown = peak_equity - df_signals['Equity']
        # Calculate percentage drawdown relative to the preceding peak
        # Avoid division by zero where peak_equity might be 0 (although with starting capital 10000 it shouldn't be)
        percentage_drawdown = (drawdown / peak_equity) * 100
        # Max drawdown percentage is the maximum value in the percentage_drawdown series
        max_drawdown_percentage = percentage_drawdown.max() if not percentage_drawdown.empty else 0.0


    # Calculate Profitable Trades Percentage
    profitable_trades_count = 0
    total_trades_count = 0

    # Use PnL from the df_signals DataFrame's sell signals for accurate calculation
    sell_signals_with_pnl = df_signals[df_signals['Signal'] == 'SELL'].dropna(subset=['PnL'])
    if not sell_signals_with_pnl.empty:
         profitable_trades_count = sell_signals_with_pnl[sell_signals_with_pnl['PnL'] > 0].shape[0]
         total_trades_count = sell_signals_with_pnl.shape[0]


    profitable_trades_percentage = (profitable_trades_count / total_trades_count * 100) if total_trades_count > 0 else 0


    summary_metrics = {
        "Starting Capital": starting_capital,
        "Ending Capital": ending_capital,
        "Max Drawdown (%)": max_drawdown_percentage,
        "Profitable Trades (%)": profitable_trades_percentage,
        "Profitable Trades Count": profitable_trades_count,
        "Total Trades Count": total_trades_count
    }

    return summary_metrics, trade_df