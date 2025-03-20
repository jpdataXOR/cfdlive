import requests
import random
import string
import time
import json
import pandas as pd

def generate_jsonp():
    """Generate a random JSONP callback name."""
    return "_callbacks____" + "".join(random.choices(string.ascii_letters + string.digits, k=8))

def get_current_utc_timestamp():
    """Get current UTC timestamp in milliseconds."""
    return str(int(time.time() * 1000))

def extract_json_from_jsonp(jsonp_response):
    """Extract JSON data from a JSONP response."""
    start_idx = jsonp_response.find("(") + 1
    end_idx = jsonp_response.rfind(")")

    if start_idx > 0 and end_idx > start_idx:
        try:
            json_data = jsonp_response[start_idx:end_idx]
            return json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON Decoding Error: {e}")
    else:
        raise ValueError("Invalid JSONP response format")

def fetch_stock_indices_data(instrument, offer_side="B", interval="15MIN", limit=25, time_direction="P"):
    """
    Fetch stock indices data from Dukascopy.

    Parameters:
    - instrument (str): The financial instrument (e.g., "EUR/USD").
    - offer_side (str): The offer side, "B" for bid or "A" for ask. Default is "B".
    - interval (str): The data interval (e.g., "1MIN", "1H"). Default is "15MIN".
    - limit (int): The number of data points to fetch. Default is 10.
    - time_direction (str): The time direction, "P" for past or "N" for next. Default is "P".

    Returns:
    - pd.DataFrame: DataFrame containing the stock indices data.
    """
    timestamp = get_current_utc_timestamp()
    jsonp_callback = generate_jsonp()

    url = f"https://freeserv.dukascopy.com/2.0/index.php?path=chart%2Fjson3&instrument={instrument}&offer_side={offer_side}&interval={interval}&splits=true&stocks=true&limit={limit}&time_direction={time_direction}&timestamp={timestamp}&jsonp={jsonp_callback}"

    headers = {
        "authority": "freeserv.dukascopy.com",
        "accept": "*/*",
        "referer": "https://freeserv.dukascopy.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "no-cors"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        jsonp_text = response.text
        json_data = extract_json_from_jsonp(jsonp_text)
        
        # Convert to DataFrame and rename columns to match yfinance format
        df = pd.DataFrame(json_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.rename(columns={
            "timestamp": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)
        df.set_index("Date", inplace=True)
        return df
    else:
        response.raise_for_status()