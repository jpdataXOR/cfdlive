import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def display_chart_and_table(df: pd.DataFrame, df_signals: pd.DataFrame):
    """
    Display candlestick chart with strategy signals and equity curve.
    Also display a results summary table with debug prints.
    """
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
    buy_signals = df_signals[df_signals['Signal'] == 'BUY']
    fig.add_trace(go.Scatter(
        x=buy_signals.index,
        y=buy_signals['BuyPrice'],
        mode='markers',
        marker=dict(color='green', symbol='triangle-up', size=10),
        name='Buy'
    ))

    # Sell signals
    sell_signals = df_signals[df_signals['Signal'] == 'SELL']
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
    st.plotly_chart(fig, use_container_width=True)

    # Equity Curve Plot (only if Equity column exists)
    if 'Equity' in df_signals.columns:
        equity_fig = go.Figure()
        equity_fig.add_trace(go.Scatter(
            x=df_signals.index,
            y=df_signals['Equity'],
            mode='lines',
            name='Equity Curve',
            line=dict(color='blue')
        ))
        equity_fig.update_layout(
            title="📈 Equity Curve",
            xaxis_title="Date",
            yaxis_title="Equity",
            height=300
        )
        st.plotly_chart(equity_fig, use_container_width=True)

    # Debugging Output
    st.subheader("🧪 Debug: Sell Signals Data")
    st.dataframe(sell_signals.head(10))

    if 'PnL' in sell_signals.columns:
        st.write("🧪 Sample PnL values:", sell_signals['PnL'].head(10))

    if 'Drawdown' in df_signals.columns:
        st.write("🧪 Sample Drawdown values:", df_signals['Drawdown'].dropna().head(10))

    # Summary Table
    trades = sell_signals.dropna(subset=['PnL']) if 'PnL' in sell_signals.columns else pd.DataFrame()
    total_pnl = trades['PnL'].sum() if not trades.empty else 0
    num_trades = len(trades)
    avg_pnl = trades['PnL'].mean() if num_trades > 0 else 0
    max_drawdown = df_signals['Drawdown'].min() if 'Drawdown' in df_signals.columns else 0

    results = pd.DataFrame({
        'Metric': ['Total Trades', 'Total PnL', 'Average PnL per Trade', 'Max Drawdown'],
        'Value': [num_trades, round(total_pnl, 2), round(avg_pnl, 2), round(max_drawdown, 2)]
    })

    st.subheader("📋 Strategy Results Summary")
    st.dataframe(results)
