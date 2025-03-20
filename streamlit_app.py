import streamlit as st
import requests
import random
import string
import time
import json
import pandas as pd
import plotly.graph_objects as go

# Function to generate a random JSONP callback name
def generate_jsonp():
    jsonp_name = "_callbacks____" + "".join(random.choices(string.ascii_letters + string.digits, k=8))
    st.write(f"🔹 Generated JSONP Callback: `{jsonp_name}`")
    return jsonp_name

# Function to get current UTC timestamp in milliseconds
def get_current_utc_timestamp():
    timestamp = str(int(time.time() * 1000))
    st.write(f"🔹 Current UTC Timestamp: `{timestamp}`")
    return timestamp

# Function to extract JSON from JSONP response
def extract_json_from_jsonp(jsonp_response):
    st.write("🔹 Extracting JSON from JSONP response...")
    
    # Find the first and last parentheses
    start_idx = jsonp_response.find("(") + 1
    end_idx = jsonp_response.rfind(")")

    if start_idx > 0 and end_idx > start_idx:
        try:
            json_data = jsonp_response[start_idx:end_idx]  # Extract the JSON inside parentheses
            return json.loads(json_data)  # Convert to Python object
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON Decoding Error: {e}")
            return None
    else:
        st.error("❌ Invalid JSONP response format")
        return None

# Streamlit UI
st.title("📊 Dukascopy JSONP Data Fetcher & Plotter")

# User-configurable URL parameters
instrument = st.text_input("Instrument (e.g., EUR/USD)", "EUR/USD")
offer_side = st.selectbox("Offer Side", ["B", "A"], index=0)
interval = st.text_input("Interval (e.g., 1MIN)", "1MIN")
limit = st.number_input("Limit", min_value=1, max_value=1000, value=249)
time_direction = st.selectbox("Time Direction", ["P", "F"], index=0)

# Get timestamp and JSONP callback name
timestamp = get_current_utc_timestamp()
jsonp_callback = generate_jsonp()

# Construct URL
url = f"https://freeserv.dukascopy.com/2.0/index.php?path=chart%2Fjson3&instrument={instrument}&offer_side={offer_side}&interval={interval}&splits=true&stocks=true&limit={limit}&time_direction={time_direction}&timestamp={timestamp}&jsonp={jsonp_callback}"

st.write(f"🔹 Generated URL: `{url}`")

# Fetch Data Button
if st.button("Fetch Data"):
    headers = {
        "authority": "freeserv.dukascopy.com",
        "accept": "*/*",
        "referer": "https://freeserv.dukascopy.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "no-cors"
    }

    try:
        st.write("🔹 Sending Request...")
        response = requests.get(url, headers=headers)
        st.write(f"🔹 Response Status Code: `{response.status_code}`")

        if response.status_code == 200:
            jsonp_text = response.text
            st.code(jsonp_text[:500] + "...", language="json")  # Display partial response for debugging

            # Extract JSON data from JSONP response
            json_data = extract_json_from_jsonp(jsonp_text)

            if json_data:
                st.write("✅ Successfully Extracted Data!")

                # Convert to DataFrame
                df = pd.DataFrame(json_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")  # Convert timestamp

                st.write("🔹 Displaying first 5 rows of data:")
                st.dataframe(df.head())

                # Plot Candlestick Chart with Plotly
                fig = go.Figure(data=[go.Candlestick(
                    x=df["timestamp"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    name="Price",
                )])

                fig.update_layout(title=f"Candlestick Chart for {instrument}", xaxis_title="Timestamp", yaxis_title="Price")
                st.plotly_chart(fig)

            else:
                st.error("❌ Failed to extract JSON data.")

        else:
            st.error(f"❌ Error: {response.status_code} - {response.reason}")

    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
