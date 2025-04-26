import pandas as pd
import numpy as np

def dumb_buy_sell_strategy(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
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
    units = 0
    trade_log = []
    equity_at_buy = 0 # To track capital invested in a trade


    for i in range(1, len(df)):
        # Carry forward the equity and drawdown from the previous step
        df.loc[df.index[i], 'Equity'] = equity
        df.loc[df.index[i], 'Drawdown'] = equity - peak_equity


        if i % 10 == 0 and position is None:
            df.loc[df.index[i], 'Signal'] = 'BUY'
            entry_price = df['Close'].iloc[i]
            # Invest all capital
            if entry_price > 0: # Avoid division by zero
                units = equity / entry_price
                df.loc[df.index[i], 'BuyPrice'] = entry_price # Still log the price per unit
                position = 'long'
                equity_at_buy = equity # Record capital at the time of buy
                # Log the buy trade
                trade_log.append({
                    'Date': df.index[i],
                    'Capital': equity, # Capital before the trade
                    'Buy/sell': 'BUY',
                    'Invested in this trade': equity_at_buy # Invested amount is the total capital
                })


        elif i % 10 == 5 and position == 'long':
            df.loc[df.index[i], 'Signal'] = 'SELL'
            sell_price = df['Close'].iloc[i]
            df.loc[df.index[i], 'SellPrice'] = sell_price
            # Calculate PnL based on units held
            pnl = (sell_price - entry_price) * units
            df.loc[df.index[i], 'PnL'] = pnl
            equity += pnl
            peak_equity = max(peak_equity, equity)
            position = None
            units = 0 # Reset units after selling
            # Log the sell trade
            trade_log.append({
                'Date': df.index[i],
                'Capital': equity, # Capital after the trade
                'Buy/sell': 'SELL',
                'Invested in this trade': equity_at_buy # Amount invested was the capital before this trade (CORRECTED)
            })
            equity_at_buy = 0 # Reset invested capital tracking


    return df, trade_log

def moving_average_crossover_strategy(df: pd.DataFrame, short_window=5, long_window=20) -> tuple[pd.DataFrame, list]:
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
    units = 0
    trade_log = []
    equity_at_buy = 0 # To track capital invested in a trade


    for i in range(long_window, len(df)):
        # Carry forward the equity and drawdown from the previous step if no trade happens
        df.loc[df.index[i], 'Equity'] = equity
        df.loc[df.index[i], 'Drawdown'] = equity - peak_equity


        if df['SMA_short'].iloc[i] > df['SMA_long'].iloc[i] and position is None:
            df.loc[df.index[i], 'Signal'] = 'BUY'
            entry_price = df['Close'].iloc[i]
            # Invest all capital
            if entry_price > 0: # Avoid division by zero
                units = equity / entry_price
                df.loc[df.index[i], 'BuyPrice'] = entry_price # Still log the price per unit
                position = 'long'
                equity_at_buy = equity # Record capital at the time of buy
                # Log the buy trade
                trade_log.append({
                    'Date': df.index[i],
                    'Capital': equity, # Capital before the trade
                    'Buy/sell': 'BUY',
                    'Invested in this trade': equity_at_buy # Invested amount is the total capital
                })

        elif df['SMA_short'].iloc[i] < df['SMA_long'].iloc[i] and position == 'long':
            df.loc[df.index[i], 'Signal'] = 'SELL'
            sell_price = df['Close'].iloc[i]
            df.loc[df.index[i], 'SellPrice'] = sell_price
            # Calculate PnL based on units held
            pnl = (sell_price - entry_price) * units
            df.loc[df.index[i], 'PnL'] = pnl
            equity += pnl
            peak_equity = max(peak_equity, equity)
            position = None
            units = 0 # Reset units after selling
            # Log the sell trade
            trade_log.append({
                'Date': df.index[i],
                'Capital': equity, # Capital after the trade
                'Buy/sell': 'SELL',
                'Invested in this trade': equity_at_buy # Amount invested was the capital before this trade (CORRECTED)
            })
            equity_at_buy = 0 # Reset invested capital tracking


    return df, trade_log


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
) -> tuple[pd.DataFrame, list]:
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
    units = 0
    cooldown_counter = 0
    trade_log = []
    equity_at_buy = 0 # To track capital invested in a trade


    def f_up(closes, i):
        return closes[i] > closes[i + 1]

    closes = df['Close'].values

    for i in range(min_bars, len(df) - proj_len - pattern_offset - pattern_len):
         # Carry forward the equity and drawdown from the previous step
         df.loc[df.index[i], 'Equity'] = equity
         df.loc[df.index[i], 'Drawdown'] = equity - peak_equity


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

             # Carry forward equity/drawdown for steps between signal calculation and trade execution
             if i < idx: # Ensure idx is ahead of i
                  for j in range(i + 1, min(idx + 1, len(df))): # Iterate up to and including idx, but not beyond df length
                       df.loc[df.index[j], 'Equity'] = equity
                       df.loc[df.index[j], 'Drawdown'] = equity - peak_equity


             if signal_type == 'BUY' and position is None:
                 df.loc[df.index[idx], 'Signal'] = 'BUY'
                 entry_price = df['Close'].iloc[idx]
                  # Invest all capital
                 if entry_price > 0: # Avoid division by zero
                     units = equity / entry_price
                     df.loc[df.index[idx], 'BuyPrice'] = entry_price # Still log the price per unit
                     position = 'long'
                     cooldown_counter = cooldown
                     equity_at_buy = equity # Record capital at the time of buy
                      # Log the buy trade
                     trade_log.append({
                         'Date': df.index[idx],
                         'Capital': equity, # Capital before the trade
                         'Buy/sell': 'BUY',
                         'Invested in this trade': equity_at_buy # Invested amount is the total capital
                     })


             elif signal_type == 'SELL' and position == 'long':
                 df.loc[df.index[idx], 'Signal'] = 'SELL'
                 sell_price = df['Close'].iloc[idx]
                 df.loc[df.index[idx], 'SellPrice'] = sell_price
                 # Calculate PnL based on units held
                 pnl = (sell_price - entry_price) * units
                 df.loc[df.index[idx], 'PnL'] = pnl
                 equity += pnl
                 peak_equity = max(peak_equity, equity)
                 position = None
                 units = 0 # Reset units after selling
                 cooldown_counter = cooldown
                  # Log the sell trade
                 trade_log.append({
                     'Date': df.index[idx],
                     'Capital': equity, # Capital after the trade
                     'Buy/sell': 'SELL',
                     'Invested in this trade': equity_at_buy # Amount invested was the capital before this trade (CORRECTED)
                 })
                 equity_at_buy = 0 # Reset invested capital tracking

         else:
              # If no signal and no trade, ensure equity and drawdown are carried forward
              df.loc[df.index[i], 'Equity'] = equity
              df.loc[df.index[i], 'Drawdown'] = equity - peak_equity


    # After the loop, update the remaining equity and drawdown values
    # Find the last index potentially processed within the loop logic (either through signal or just iteration)
    start_idx_after_loop = min_bars # Initialize with min_bars
    if len(df) > proj_len + pattern_offset + pattern_len:
         start_idx_after_loop = max(min_bars, len(df) - proj_len - pattern_offset - pattern_len)

    if start_idx_after_loop < len(df):
         for i in range(start_idx_after_loop, len(df)):
              df.loc[df.index[i], 'Equity'] = equity
              df.loc[df.index[i], 'Drawdown'] = equity - peak_equity


    return df, trade_log