from datetime import datetime, timedelta
import yfinance as yf

# Limit to the last 30 days
default_start_date = (datetime.today() - timedelta(days=29)).strftime("%Y-%m-%d")

data = yf.download(
    ["CSPX.AS"],
    start=default_start_date,
    end=datetime.today().strftime("%Y-%m-%d"),
    group_by="ticker",
    progress=False,
    interval="60m"
)



print(data)
