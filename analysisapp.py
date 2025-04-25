import pandas as pd
import numpy as np

def dumb_buy_sell_strategy(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Signal'] = None
    df['BuyPrice'] = None
    df['SellPrice'] = None
    df['PnL'] = None
    df['Equity'] = 10000
    df['Drawdown'] = 0

    equity = 10000
    peak_equity = equity
    position = None
    entry_price = 0

    for i in range(1, len(df)):
        if i % 10 == 0 and position is None:
            df.loc[df.index[i], 'Signal'] = 'BUY'
            df.loc[df.index[i], 'BuyPrice'] = df['Close'].iloc[i]
            entry_price = df['Close'].iloc[i]
            position = 'long'

        elif i % 10 == 5 and position == 'long':
            df.loc[df.index[i], 'Signal'] = 'SELL'
            df.loc[df.index[i], 'SellPrice'] = df['Close'].iloc[i]
            pnl = df['Close'].iloc[i] - entry_price
            df.loc[df.index[i], 'PnL'] = pnl
            equity += pnl
            df.loc[df.index[i], 'Equity'] = equity
            peak_equity = max(peak_equity, equity)
            df.loc[df.index[i], 'Drawdown'] = equity - peak_equity
            position = None

        df.loc[df.index[i], 'Equity'] = equity
        df.loc[df.index[i], 'Drawdown'] = equity - peak_equity

    return df

def moving_average_crossover_strategy(df: pd.DataFrame, short_window=5, long_window=20) -> pd.DataFrame:
    df = df.copy()
    df['SMA_short'] = df['Close'].rolling(window=short_window).mean()
    df['SMA_long'] = df['Close'].rolling(window=long_window).mean()
    df['Signal'] = None
    df['BuyPrice'] = None
    df['SellPrice'] = None
    df['PnL'] = None
    df['Equity'] = 10000
    df['Drawdown'] = 0

    equity = 10000
    peak_equity = equity
    position = None
    entry_price = 0

    for i in range(long_window, len(df)):
        if df['SMA_short'].iloc[i] > df['SMA_long'].iloc[i] and position is None:
            df.loc[df.index[i], 'Signal'] = 'BUY'
            df.loc[df.index[i], 'BuyPrice'] = df['Close'].iloc[i]
            entry_price = df['Close'].iloc[i]
            position = 'long'

        elif df['SMA_short'].iloc[i] < df['SMA_long'].iloc[i] and position == 'long':
            df.loc[df.index[i], 'Signal'] = 'SELL'
            df.loc[df.index[i], 'SellPrice'] = df['Close'].iloc[i]
            pnl = df['Close'].iloc[i] - entry_price
            df.loc[df.index[i], 'PnL'] = pnl
            equity += pnl
            df.loc[df.index[i], 'Equity'] = equity
            peak_equity = max(peak_equity, equity)
            df.loc[df.index[i], 'Drawdown'] = equity - peak_equity
            position = None

        df.loc[df.index[i], 'Equity'] = equity
        df.loc[df.index[i], 'Drawdown'] = equity - peak_equity

    return df



def projection_pattern_strategy(
    df: pd.DataFrame,
    pattern_len=4,
    proj_len=10,
    pattern_offset=1,
    max_matches=10,
    buy_threshold=2.0,
    sell_threshold=2.0,
    cooldown=5,
    min_bars=100
) -> pd.DataFrame:
    df = df.copy()
    df['Signal'] = None
    df['BuyPrice'] = None
    df['SellPrice'] = None
    df['PnL'] = None
    df['Equity'] = 10000
    df['Drawdown'] = 0

    equity = 10000
    peak_equity = equity
    position = None
    entry_price = 0
    cooldown_counter = 0

    def f_up(closes, i):
        return closes[i] > closes[i + 1]

    closes = df['Close'].values

    for i in range(min_bars, len(df) - proj_len - pattern_offset - pattern_len):
        if cooldown_counter > 0:
            cooldown_counter -= 1
            continue

        base_idx = i - pattern_offset
        pattern = [f_up(closes, base_idx + j) for j in range(pattern_len)]
        matches = []
        base_price = closes[base_idx]

        for j in range(pattern_offset + pattern_len, i - proj_len):
            match = [f_up(closes, j + k) for k in range(pattern_len)]
            if match == pattern:
                pct_changes = [(closes[j + k] - closes[j + k - 1]) / closes[j + k - 1] for k in range(pattern_len, pattern_len + proj_len)]
                matches.append(pct_changes)
                if len(matches) >= max_matches:
                    break

        if matches:
            proj_matrix = np.array(matches)
            avg_proj = np.mean(proj_matrix, axis=0)
            avg_direction = np.mean(avg_proj) * 100  # convert to percent

            # Decision logic
            signal_type = None
            if avg_direction > buy_threshold:
                signal_type = 'BUY'
            elif avg_direction < -sell_threshold:
                signal_type = 'SELL'

            idx = i + proj_len
            if idx >= len(df):
                break

            if signal_type == 'BUY' and position is None:
                df.loc[df.index[idx], 'Signal'] = 'BUY'
                df.loc[df.index[idx], 'BuyPrice'] = df['Close'].iloc[idx]
                entry_price = df['Close'].iloc[idx]
                position = 'long'
                cooldown_counter = cooldown

            elif signal_type == 'SELL' and position == 'long':
                df.loc[df.index[idx], 'Signal'] = 'SELL'
                df.loc[df.index[idx], 'SellPrice'] = df['Close'].iloc[idx]
                pnl = df['Close'].iloc[idx] - entry_price
                df.loc[df.index[idx], 'PnL'] = pnl
                equity += pnl
                df.loc[df.index[idx], 'Equity'] = equity
                peak_equity = max(peak_equity, equity)
                df.loc[df.index[idx], 'Drawdown'] = equity - peak_equity
                position = None
                cooldown_counter = cooldown

        df.loc[df.index[i], 'Equity'] = equity
        df.loc[df.index[i], 'Drawdown'] = equity - peak_equity

    return df

