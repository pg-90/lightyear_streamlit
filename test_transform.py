from transform import TickerAnalyzer

raw_folder = "data/tickers"
analyzed_folder = "data/analyzed"


analyzer = TickerAnalyzer(raw_folder=raw_folder, analyzed_folder=analyzed_folder)

for ticker in ["GMVM.DE"]:
    analyzer.preprocess_and_analyze(ticker)
