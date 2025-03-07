import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone
from extractor import Extractor
from transform import TickerAnalyzer
import matplotlib.pyplot as plt


def load_and_filter_analyzed_data(analyzed_folder):
    """Load all CSVs, add a 'symbol' column, and filter last X days."""
    all_data = []
    for filename in os.listdir(analyzed_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(analyzed_folder, filename)
            df = pd.read_csv(file_path)
            df["symbol"] = filename.split(".")[0]
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True)


# Streamlit UI
st.title("Lightyear Analysis App")

# Default settings
default_start_date = (datetime.today() - timedelta(days=151)).strftime("%Y-%m-%d")
default_days = 2
default_rsi_buy = 40
default_cci_buy = -85
default_rsi_sell = 65
default_cci_sell = 90

# Load tickers from JSON
json_file = "data/lightyear_yfinance_etf_data.json"
if not os.path.exists(json_file):
    st.error(f"JSON file {json_file} not found!")
    st.stop()

with open(json_file, "r") as file:
    tickers_data = json.load(file)

tickers = list(tickers_data.values())
symbols = list(tickers_data.keys())  # Extract ticker symbols
symbols.sort()
st.write(f"Loaded {len(tickers)} tickers from {json_file}")

# Paths
raw_folder = "data/tickers"
analyzed_folder = "data/analyzed"

# Ensure output directories exist
os.makedirs(analyzed_folder, exist_ok=True)
os.makedirs(raw_folder, exist_ok=True)

# User input and filters inside expandable sections
with st.expander("Set Thresholds & Filtering Options"):
    col1, col2 = st.columns(2)
    with col1:
        rsi_buy = st.number_input("RSI Buy Threshold", value=default_rsi_buy)
        cci_buy = st.number_input("CCI Buy Threshold", value=default_cci_buy)
    with col2:
        rsi_sell = st.number_input("RSI Sell Threshold", value=default_rsi_sell)
        cci_sell = st.number_input("CCI Sell Threshold", value=default_cci_sell)

    start_date = st.date_input(
        "Select Start Date", datetime.strptime(default_start_date, "%Y-%m-%d")
    )
    days = st.slider("Filter last X days:", 1, 365, default_days)

# Step buttons in an expander for data operations
with st.expander("Data Operations (Extract, Analyze, Clean-Up)"):
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

    # Step 3: Clean-Up Data
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

# Filter selection inside an expander
with st.expander("Select Filter Criteria & Symbols"):
    selected_criteria = st.multiselect(
        "Select Criteria to Filter", ["buy", "sell", "hold"], default=["buy", "sell"]
    )
    selected_symbols = st.multiselect(
        "Select Tickers to Filter", symbols, default=symbols
    )

    # Step 4: Load and Filter Data (only after criteria is selected)
    if st.button("Load & Filter Data"):
        st.write("Loading and filtering data, please wait...")

        filtered_data = load_and_filter_analyzed_data(analyzed_folder)

        # Filter last X days
        today = datetime.now(timezone.utc)
        days_ago = today - timedelta(days=days)

        filtered_data["date"] = pd.to_datetime(
            filtered_data["date"], errors="coerce"
        ).dt.tz_localize(None)
        days_ago = days_ago.replace(tzinfo=None)
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
            col
            for col in result_df.columns
            if col not in ["date", "symbol", "criteria"]
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


# Plot Data - Create another expander for this section
with st.expander("Plot Selected Symbol Data"):
    # Step 5: Plot Selected Symbol Data
    col_symbol, col_date_range = st.columns([1, 2])

    with col_symbol:
        selected_plot_symbol = st.selectbox("Select Symbol to Plot", symbols)

    with col_date_range:
        start_date_plot = st.date_input(
            "Start Date", default_start_date
        )
        start_date_plot = st.date_input("Start Date", value=datetime.strptime(default_start_date, "%Y-%m-%d").date())

        end_date_plot = datetime.today()  # Set end date to today's date

    # Ensure both start_date_plot and end_date_plot are datetime.date objects
    if isinstance(
        start_date_plot, datetime
    ):  # Check if it's a datetime.datetime object
        start_date_plot = start_date_plot.date()

    end_date_plot = (
        end_date_plot.date()
    )  # If end_date_plot is a datetime.datetime, convert it to datetime.date

    # Calculate the difference between the start and end dates
    date_diff = (end_date_plot - start_date_plot).days
    # Determine whether to display data daily or weekly
    interval = "weekly" if date_diff > 14 else "daily"

    if interval == "weekly":
        st.write(
            "The date range is more than 2 weeks, so the data will be displayed weekly."
        )
    else:
        st.write(
            "The date range is within 2 weeks, so the data will be displayed daily."
        )

    # Button to plot data
    if st.button("Plot Data"):
        st.write(f"Generating plots for {selected_plot_symbol}...")

        # Load all data
        df = load_and_filter_analyzed_data(analyzed_folder)

        # Convert date column to datetime
        df["date"] = pd.to_datetime(df["date"])

        # Filter for the selected symbol
        df_symbol = df[df["symbol"] == selected_plot_symbol]

        # Apply date range filter (use today's date for the end date)
        df_symbol = df_symbol[
            (df_symbol["date"] >= pd.to_datetime(start_date_plot))
            & (df_symbol["date"] <= pd.to_datetime(end_date_plot))
        ]

        # Check if data exists after filtering
        if df_symbol.empty:
            st.error(
                f"No data available for {selected_plot_symbol} in the selected date range."
            )
        else:
            # Resample the data based on the interval (daily or weekly)
            if interval == "weekly":
                df_symbol = df_symbol.resample("W-Mon", on="date").agg(
                    {
                        "close": "last",
                        "rsi_14": "last",
                        "cci_25": "last",
                        "ma_9": "last",
                        "ma_50": "last",
                    }
                )
            else:
                df_symbol = df_symbol.set_index("date")

            # Create subplots
            fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

            # Plot Closing Price & Moving Averages
            has_ma_50 = "ma_50" in df_symbol.columns
            axes[0].plot(
                df_symbol.index, df_symbol["close"], label="Close Price", color="blue"
            )
            axes[0].plot(
                df_symbol.index,
                df_symbol["ma_9"],
                label="MA 9",
                linestyle="dashed",
                color="orange",
            )
            if has_ma_50:
                axes[0].plot(
                    df_symbol.index,
                    df_symbol["ma_50"],
                    label="MA 50",
                    linestyle="dashed",
                    color="green",
                )
            axes[0].set_title(f"{selected_plot_symbol} Price and MAs")
            axes[0].legend(loc="best")

            # Plot RSI
            axes[1].plot(
                df_symbol.index, df_symbol["rsi_14"], label="RSI 14", color="purple"
            )
            axes[1].axhline(30, color="red", linestyle="--")
            axes[1].axhline(70, color="red", linestyle="--")
            axes[1].set_title("RSI 14")
            axes[1].legend(loc="best")

            # Plot CCI
            axes[2].plot(
                df_symbol.index, df_symbol["cci_25"], label="CCI 25", color="green"
            )
            axes[2].axhline(100, color="red", linestyle="--")
            axes[2].axhline(-100, color="red", linestyle="--")
            axes[2].set_title("CCI 25")
            axes[2].legend(loc="best")

            plt.tight_layout()
            st.pyplot(fig)
            st.write(
                f"### Data for {selected_plot_symbol} from {start_date_plot} to {end_date_plot}"
            )
