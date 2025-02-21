from datetime import datetime, timedelta
import yfinance as yf

from extractor import Extractor

start_date = (datetime.today() - timedelta(days=151)).strftime("%Y-%m-%d")

extractor = Extractor(
    tickers=["GMVM.DE"],
    start_date=str(start_date),
    end_date=datetime.now().strftime("%Y-%m-%d"),
    target_folder="data/tickers",
)
extractor.extract_data()
