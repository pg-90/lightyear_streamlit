import json

DATA_FOLDER = "data"
# Define the mapping rules for Yahoo Finance
exchange_mapping = {
    "AEX": ".AS",  # Euronext Amsterdam
    "XETRA": ".DE",  # Deutsche Börse XETRA
    "PAR": ".PA",  # Euronext Paris
}


# Function to convert an ETF ticker to its Yahoo Finance equivalent
def convert_to_yfinance(ticker, exchange):
    if exchange in exchange_mapping:
        return ticker + exchange_mapping[exchange]
    return ticker  # If the exchange is not recognized, leave it as is


# Load the JSON file
with open(f"{DATA_FOLDER}/lightyear_raw_etf_data.json", "r") as file:
    etf_data = json.load(file)

# Convert the values to Yahoo Finance tickers
yfinance_data = {}
for ticker, exchange in etf_data.items():
    yfinance_data[ticker] = convert_to_yfinance(ticker, exchange)

# Save the updated data back to a new JSON file
with open(f"{DATA_FOLDER}/lightyear_yfinance_etf_data.json", "w") as file:
    json.dump(yfinance_data, file, indent=4)

print("Updated data saved to 'lightyear_yfinance_etf_data.json'")
