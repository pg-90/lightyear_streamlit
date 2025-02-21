"""Extract a symbol(s)"""

from typing import List
import os
import re
import yfinance as yf
from yfinance.data import YfData
import requests

# Define a modern User-Agent header
NEW_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Monkey-patch the YfData class to use the new headers
class PatchedYfData(YfData):
    def _fetch(self, url, params=None, **kwargs):
        if "headers" not in kwargs:
            kwargs["headers"] = NEW_HEADERS
        return super()._fetch(url, params=params, **kwargs)

# Replace the default YfData instance with our patched version
patched_data_instance = PatchedYfData()
patched_data_instance.session = requests.Session()
yf.shared._data = patched_data_instance

class Extractor:
    """This is the extractor Class"""

    def __init__(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        target_folder: str = "data/tickers",
    ):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.target_folder = target_folder

        # Create the target folder if it doesn't exist
        print(self.target_folder)
        if not os.path.exists(self.target_folder):
            print(f"Creating folder {self.target_folder}...")
            os.makedirs(self.target_folder, exist_ok=True)

    def clean_col(self, col):
        """
        Clean the column name by:
        - Converting to lower-case.
        - Removing any trailing suffix that resembles a domain (e.g. 'iqq0.de').
        - Removing underscores.
        """
        # If col is a tuple, join the elements first.
        if isinstance(col, tuple):
            col = "_".join(str(item) for item in col)
        # Convert to lower case.
        col = col.lower()
        # Remove any trailing suffix that resembles a domain pattern:
        # This regex removes a pattern at the end that starts with alphanumeric characters,
        # followed by a dot and two or more letters (e.g., 'iqq0.de', 'abc123.com').
        col = re.sub(r'[a-z0-9]+\.[a-z]{2,}$', '', col)
        # Remove any remaining underscores.
        col = col.replace('_', '')
        return col

    def extract_data(self) -> dict:
        """Downloads ticker data from Yahoo Finance"""
        result_data = {}
        for ticker in self.tickers:
            # Download stock data using yfinance with the patched headers
            stock_data = yf.download(
                ticker,
                start=self.start_date,
                end=self.end_date,
                interval="60m"
            )
            # If the data is nested by ticker symbol, extract it accordingly.
            if ticker in stock_data:
                stock_data = stock_data[ticker]

            # Reset index
            stock_data.reset_index(inplace=True)

            # Rename columns using the clean_col function.
            stock_data.columns = [self.clean_col(col) for col in stock_data.columns]

            # Save the data to a CSV file in the target folder
            file_path = os.path.join(self.target_folder, f"{ticker}.csv")
            stock_data.to_csv(file_path, index=False)
            print(f"Saved {ticker} data to {file_path}")

            result_data[ticker] = stock_data

        return result_data
