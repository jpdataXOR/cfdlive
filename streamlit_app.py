import streamlit as st
import requests
import random
import string
import time

# Function to generate a random JSONP callback name
def generate_jsonp():
    return "_callbacks____" + "".join(random.choices(string.ascii_letters + string.digits, k=8))

# Function to get current UTC timestamp in milliseconds
def get_current_utc_timestamp():
    return str(int(time.time() * 1000))

# Streamlit UI
st.title("Dukascopy JSONP Data Fetcher")

# User-configurable URL parameters
instrument = st.text_input("Instrument (e.g., EUR/USD)", "EUR/USD")
offer_side = st.selectbox("Offer Side", ["B", "A"], index=0)
interval = st.text_input("Interval (e.g., 1MIN)", "1MIN")
limit = st.number_input("Limit", min_value=1, max_value=1000, value=249)
time_direction = st.selectbox("Time Direction", ["P", "F"], index=0)

# Automatically use the current UTC timestamp
timestamp = get_current_utc_timestamp()
st.write(f"Using current UTC timestamp: `{timestamp}`")

# Generate random JSONP name
jsonp_callback = generate_jsonp()

# Construct URL
url = f"https://freeserv.dukascopy.com/2.0/index.php?path=chart%2Fjson3&instrument={instrument}&offer_side={offer_side}&interval={interval}&splits=true&stocks=true&limit={limit}&time_direction={time_direction}&timestamp={timestamp}&jsonp={jsonp_callback}"

st.write("Generated URL:", url)

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
        response = requests.get(url, headers=headers)
        st.subheader("Response:")
        st.code(response.text, language="json")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

st.write(f"Using JSONP callback: `{jsonp_callback}`")
