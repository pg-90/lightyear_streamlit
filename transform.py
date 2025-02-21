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

        # Adjust the file path to match the expected pattern: ticker.csv
        file_name = f"{ticker}.csv"
        file_path = os.path.join(self.raw_folder, file_name)

        if not os.path.exists(file_path):
            print(f"Raw data for {ticker} not found at {file_path}!")
            return

        # Load the raw ticker data with needed columns
        ticker_data = pd.read_csv(
            file_path,
            usecols=["datetime", "close", "high", "low"],
            parse_dates=["datetime"],
        )
        ticker_data["date"] = ticker_data["datetime"].dt.date
        aggregated_df = ticker_data.groupby("date").last().reset_index()
        aggregated_df = aggregated_df[["date", "close", "high", "low"]]

        # Create a full date range from the minimum to the maximum date
        full_date_range = pd.date_range(
            start=aggregated_df.date.min(), end=aggregated_df.date.max()
        )
        # Reindex and forward fill missing values
        main_df = aggregated_df.set_index("date").reindex(full_date_range)
        main_df.ffill(inplace=True)
        main_df.index.name = "date"  # optional, to keep index name consistent

        # Calculate percentage change on close
        main_df["pct_change"] = main_df["close"].pct_change() * 100

        # Compute CCI on the aggregated data from main_df
        cci = CCIIndicator(
            high=main_df["high"],
            low=main_df["low"],
            close=main_df["close"],
            window=25,
            constant=0.015,
        )
        main_df["cci_25"] = cci.cci()

        # RSI (Relative Strength Index) computed on the aggregated close values
        rsi = RSIIndicator(close=main_df["close"], window=14)
        main_df["rsi_14"] = rsi.rsi()

        # Moving Averages
        main_df["ma_9"] = main_df["close"].rolling(window=9).mean()
        main_df["ma_14"] = main_df["close"].rolling(window=14).mean()  # 14-day MA
        main_df["ma_50"] = main_df["close"].rolling(window=50).mean()  # 50-day MA

        main_df.reset_index(inplace=True)
        main_df.rename(columns={"index": "date"}, inplace=True)
        analyzed_file_path = os.path.join(self.analyzed_folder, f"{trimmed_ticker}.csv")

        cols_to_keep = [
            "date",
            "close",
            "pct_change",
            "cci_25",
            "rsi_14",
            "ma_9",
            "ma_14",
            "ma_50",
        ]

        main_df.to_csv(analyzed_file_path, index=False, columns=cols_to_keep)


# Example usage:
# analyzer = TickerAnalyzer(raw_folder="raw_data", analyzed_folder="analyzed_data")
# analyzer.preprocess_and_analyze("AAPL")
