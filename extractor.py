"""Extract a symbol(s)"""

from typing import List
import os
import yfinance as yf


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

    def extract_data(self) -> dict:
        """Downloads ticker data from Yahoo Finance"""

        for ticker in self.tickers:
            # print(f"Extracting data for {ticker}...")

            # Download stock data using yfinance
            stock_data = yf.download(
                ticker,
                start=self.start_date,
                end=self.end_date,
                group_by="ticker",
                progress=False,
                prepost=True,
                interval="60m"
            )
            stock_data = stock_data[ticker]

            # Reset index
            stock_data.reset_index(inplace=True)

            stock_data.columns = [
                c.lower().replace(" ", "_") for c in stock_data.columns
            ]
            # print(stock_data.columns)
            # Save the data to a CSV file in the target folder
            file_path = os.path.join(self.target_folder, f"{ticker}.csv")
            stock_data.to_csv(file_path, index=False)
            # print(f"Saved {ticker} data to {file_path}")

        return stock_data
