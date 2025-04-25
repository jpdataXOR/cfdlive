import pandas as pd

def run_strategy_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic dumb strategy: Buy every 5th candle, sell after 3 bars.
    This is just a placeholder to validate structure.
    Returns DataFrame with signals and PnL.
    """
    df = df.copy()
    df['Signal'] = None
    df['BuyPrice'] = None
    df['SellPrice'] = None
    df['PnL'] = None

    for i in range(0, len(df) - 4, 5):  # Every 5th bar
        buy_idx = i
        sell_idx = i + 3  # Sell after 3 bars
        if sell_idx >= len(df):
            break

        buy_price = df.iloc[buy_idx]['Close']
        sell_price = df.iloc[sell_idx]['Close']

        df.at[df.index[buy_idx], 'Signal'] = 'BUY'
        df.at[df.index[buy_idx], 'BuyPrice'] = buy_price
        df.at[df.index[sell_idx], 'SellPrice'] = sell_price
        df.at[df.index[sell_idx], 'Signal'] = 'SELL'
        df.at[df.index[sell_idx], 'PnL'] = sell_price - buy_price

    return df
