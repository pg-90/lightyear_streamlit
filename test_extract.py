from datetime import datetime, timedelta
import yfinance as yf
import json
from extractor import Extractor

start_date = (datetime.today() - timedelta(days=151)).strftime("%Y-%m-%d")

with open("data/lightyear_yfinance_etf_data.json", "r") as f:
    data = json.load(f)
    print(len(data.values()))
    
for d in data.values():
    extractor = Extractor(
        tickers=[d],
        start_date=str(start_date),
        end_date=datetime.now().strftime("%Y-%m-%d"),
        target_folder="data/tickers",
    )
    result = extractor.extract_data()
    #print(result)
## 'DBXN.DE' , 'DFND.PA', wbit.du, weth.du