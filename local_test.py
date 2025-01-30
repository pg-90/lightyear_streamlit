from extractor import Extractor
from datetime import datetime

raw_folder = "data/test"
start_date = "2025-01-01"
tickers = ["VUAA.DE", "QDVE.DE"]
end_date = datetime.now().strftime("%Y-%m-%d")


extractor = Extractor(
    tickers=tickers,
    start_date=str(start_date),
    end_date=end_date,
    target_folder=raw_folder,
)

print(f"Downloading: {tickers} -> from {start_date} to {end_date} into {raw_folder}")

extractor.extract_data()
