import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from extractor import Extractor
from transform import TickerAnalyzer

# Streamlit UI
st.title("Lightyear Analysis App")

# Default settings
default_start_date = "2025-01-01"
default_days = 4
default_rsi_buy = 35
default_cci_buy = -90
default_rsi_sell = 65
default_cci_sell = 90

# Create columns for the input boxes to display them in a 2x2 grid
col1, col2 = st.columns(2)

with col1:
    rsi_buy = st.number_input("RSI Buy Threshold", value=default_rsi_buy)
    cci_buy = st.number_input("CCI Buy Threshold", value=default_cci_buy)

with col2:
    rsi_sell = st.number_input("RSI Sell Threshold", value=default_rsi_sell)
    cci_sell = st.number_input("CCI Sell Threshold", value=default_cci_sell)

# User inputs for start date and filtering days
start_date = st.date_input(
    "Select Start Date", datetime.strptime(default_start_date, "%Y-%m-%d")
)
days = st.slider("Filter last X days:", 1, 365, default_days)

# Paths
raw_folder = "data/tickers"
analyzed_folder = "data/analyzed"
json_file = "data/lightyear_yfinance_etf_data.json"

# Load tickers from JSON
if not os.path.exists(json_file):
    st.error(f"JSON file {json_file} not found!")
    st.stop()

with open(json_file, "r") as file:
    tickers_data = json.load(file)

tickers = list(tickers_data.values())
symbols = list(tickers_data.keys())  # Extract ticker symbols
symbols.sort()
st.write(f"Loaded {len(tickers)} tickers from {json_file}")

# Ensure output directories exist
os.makedirs(analyzed_folder, exist_ok=True)
os.makedirs(raw_folder, exist_ok=True)

# Create a 1x3 grid layout for buttons
col_extract, col_analyze, col_cleanup = st.columns(3)

# Step 1: Extract Data
with col_extract:
    if st.button("Extract Data"):
        st.write("Extracting data, please wait...")

        extractor = Extractor(
            tickers=tickers,
            start_date=str(start_date),
            end_date=datetime.now().strftime("%Y-%m-%d"),
            target_folder=raw_folder,
        )

        extractor.extract_data()
        st.success("Data extraction complete.")

# Step 2: Analyze Data
with col_analyze:
    if st.button("Analyze Data"):
        st.write("Analyzing data, please wait...")

        analyzer = TickerAnalyzer(
            raw_folder=raw_folder, analyzed_folder=analyzed_folder
        )

        for ticker in tickers:
            analyzer.preprocess_and_analyze(ticker)

        st.success("All tickers processed and analyzed.")

# Step 5: Clean-Up Data
with col_cleanup:
    if st.button("Clean-Up Data"):
        st.write("Cleaning up raw and analyzed data...")

        def delete_files_in_folder(folder):
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    file_path = os.path.join(folder, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                st.write(f"Deleted all files in {folder}")
            else:
                st.write(f"Folder {folder} does not exist.")

        delete_files_in_folder(raw_folder)
        delete_files_in_folder(analyzed_folder)
        st.success("Clean-up complete.")

# Step 3: Select Filter Criteria and Symbols
selected_criteria = st.multiselect(
    "Select Criteria to Filter",
    ["buy", "sell", "hold"],
    default=["buy", "sell", "hold"],
)

# Allow the user to filter by symbols
selected_symbols = st.multiselect("Select Tickers to Filter", symbols, default=symbols)

# Step 4: Load and Filter Data (only after criteria is selected)
if st.button("Load & Filter Data"):
    st.write("Loading and filtering data, please wait...")

    def load_and_filter_analyzed_data(analyzed_folder):
        """Load all CSVs, add a 'symbol' column, and filter last X days."""
        all_data = []
        for filename in os.listdir(analyzed_folder):
            if filename.endswith(".csv"):
                file_path = os.path.join(analyzed_folder, filename)
                df = pd.read_csv(file_path)
                df["symbol"] = filename.split(".")[0]
                all_data.append(df)

        combined_data = pd.concat(all_data, ignore_index=True)
        return combined_data

    filtered_data = load_and_filter_analyzed_data(analyzed_folder)

    # Filter last X days
    today = datetime.today()
    days_ago = today - timedelta(days=days)

    filtered_data["date"] = pd.to_datetime(filtered_data["date"])
    df_filtered = filtered_data[filtered_data["date"] >= days_ago]

    # Add 'criteria' column based on user-defined thresholds
    df_filtered["criteria"] = df_filtered.apply(
        lambda row: "buy"
        if row["rsi_14"] < rsi_buy and row["cci_25"] < cci_buy
        else "sell"
        if row["rsi_14"] > rsi_sell and row["cci_25"] > cci_sell
        else "hold",
        axis=1,
    )

    # Filter data based on selected criteria and symbols (apply only if criteria are selected)
    if selected_criteria:
        result_df = df_filtered[df_filtered["criteria"].isin(selected_criteria)]
    else:
        result_df = df_filtered  # If no criteria selected, display all data

    if selected_symbols:
        result_df = result_df[result_df["symbol"].isin(selected_symbols)]

    # Format the date column to YYYY-MM-DD
    result_df["date"] = result_df["date"].dt.strftime("%Y-%m-%d")

    # Rearrange columns to print date, symbol, criteria first, then others
    ordered_columns = ["date", "symbol", "criteria"] + [
        col for col in result_df.columns if col not in ["date", "symbol", "criteria"]
    ]
    result_df = result_df[ordered_columns]

    # Display the results in an expanded table (hide index)
    st.write("### Filtered Analysis Results:")
    st.dataframe(
        result_df.sort_values(by=["date", "symbol"], ascending=[False, True]),
        use_container_width=True,  # Stretch across the full container
        hide_index=True,  # Hide the index column
        height=None,  # Allow the table to take up maximum height if necessary
    )
