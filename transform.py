import os
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import CCIIndicator


class TickerAnalyzer:
    def __init__(self, raw_folder, analyzed_folder):
        self.raw_folder = raw_folder
        self.analyzed_folder = analyzed_folder

    def preprocess_and_analyze(self, ticker):
        """Preprocess data and calculate indicators for a single ticker."""
        # Trim the ticker to remove everything after the first "."
        trimmed_ticker = ticker.split(".")[0]

        # Adjust the file path to match the expected pattern: ticker.stock.csv
        file_name = f"{ticker}.csv"
        file_path = os.path.join(self.raw_folder, file_name)

        if not os.path.exists(file_path):
            print(f"Raw data for {ticker} not found at {file_path}!")
            return

        # Load the raw ticker data
        ticker_data = pd.read_csv(file_path)

        # Convert the 'date' column to datetime format
        ticker_data["date"] = pd.to_datetime(ticker_data["date"])

        # Ensure the data is sorted by date
        ticker_data = ticker_data.sort_values(by="date")

        # Reindex to include all dates between the min and max date for the ticker
        full_date_range = pd.date_range(
            start=ticker_data["date"].min(), end=ticker_data["date"].max()
        )

        # Reindex and forward fill for stock price columns
        ticker_data = ticker_data.set_index("date").reindex(full_date_range)

        # Forward fill for 'open', 'high', 'low', 'close'
        ticker_data[["open", "high", "low", "close"]] = ticker_data[
            ["open", "high", "low", "close"]
        ].ffill()

        # Backward fill for 'volume'
        ticker_data["volume"] = ticker_data["volume"].bfill()

        # Step 3: Apply Indicators
        # CCI (Commodity Channel Index)
        cci = CCIIndicator(
            high=ticker_data["high"],
            low=ticker_data["low"],
            close=ticker_data["close"],
            window=25,
            constant=0.015,
        )

        ticker_data["pct_change"] = ticker_data["close"].pct_change() * 100

        ticker_data["cci_25"] = cci.cci()

        # RSI (Relative Strength Index)
        rsi = RSIIndicator(close=ticker_data["close"], window=14)
        ticker_data["rsi_14"] = rsi.rsi()

        # Moving Averages
        ticker_data["ma_9"] = ticker_data["close"].rolling(window=9).mean()
        ticker_data["ma_14"] = (
            ticker_data["close"].rolling(window=14).mean()
        )  # 14-day MA
        ticker_data["ma_50"] = (
            ticker_data["close"].rolling(window=50).mean()
        )  # 50-day MA

        # Reset the index back to 'date' column
        ticker_data.reset_index(inplace=True)
        ticker_data.rename(columns={"index": "date"}, inplace=True)

        # Save the analyzed data to the analyzed folder with the trimmed ticker name
        analyzed_file_path = os.path.join(self.analyzed_folder, f"{trimmed_ticker}.csv")
        ticker_data.to_csv(analyzed_file_path, index=False)
        # print(f"Saved analyzed data for {trimmed_ticker} to {analyzed_file_path}")
