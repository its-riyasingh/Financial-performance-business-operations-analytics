import json
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. Project directories
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Financial statement types
# --------------------------------------------------

STATEMENT_TYPES = {
    "income_statement": "income",
    "balance_sheet": "balance",
    "cash_flow": "cashflow"
}


# --------------------------------------------------
# 3. Load one JSON file
# --------------------------------------------------

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# 4. Convert reports to DataFrame
# --------------------------------------------------

def process_file(filepath, statement_type):

    data = load_json(filepath)

    symbol = data.get("symbol")

    annual_reports = data.get("annualReports", [])
    quarterly_reports = data.get("quarterlyReports", [])

    rows = []

    # Annual reports
    for report in annual_reports:
        row = report.copy()
        row["symbol"] = symbol
        row["period_type"] = "Annual"
        rows.append(row)

    # Quarterly reports
    for report in quarterly_reports:
        row = report.copy()
        row["symbol"] = symbol
        row["period_type"] = "Quarterly"
        rows.append(row)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    df["statement_type"] = statement_type

    return df


# --------------------------------------------------
# 5. Clean DataFrame
# --------------------------------------------------

def clean_dataframe(df):

    if df.empty:
        return df

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Convert date
    if "fiscalDateEnding" in df.columns:
        df["fiscalDateEnding"] = pd.to_datetime(
            df["fiscalDateEnding"],
            errors="coerce"
        )

    # Convert numeric-looking columns
    exclude_columns = [
        "symbol",
        "period_type",
        "statement_type",
        "fiscalDateEnding",
        "reportedCurrency"
    ]

    for column in df.columns:

        if column not in exclude_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Sort
    sort_columns = [
        column
        for column in ["symbol", "fiscalDateEnding", "period_type"]
        if column in df.columns
    ]

    if sort_columns:
        df = df.sort_values(sort_columns)

    # Reset index
    df = df.reset_index(drop=True)

    return df


# --------------------------------------------------
# 6. Process all files
# --------------------------------------------------

def main():

    print("=" * 60)
    print("FINANCIAL DATA CLEANING")
    print("=" * 60)

    all_data = {
        "income": [],
        "balance": [],
        "cashflow": []
    }

    json_files = list(RAW_DIR.glob("*.json"))

    print(f"Raw JSON files found: {len(json_files)}")

    for filepath in json_files:

        filename = filepath.stem.lower()

        statement_type = None

        for key, value in STATEMENT_TYPES.items():

            if key in filename:
                statement_type = value
                break

        if statement_type is None:
            print(f"Skipped: {filepath.name}")
            continue

        print(f"Processing: {filepath.name}")

        df = process_file(
            filepath,
            statement_type
        )

        if not df.empty:
            all_data[statement_type].append(df)

    # --------------------------------------------------
    # Combine each statement type
    # --------------------------------------------------

    for statement_type, dataframes in all_data.items():

        if not dataframes:
            continue

        combined_df = pd.concat(
            dataframes,
            ignore_index=True
        )

        combined_df = clean_dataframe(combined_df)

        output_file = (
            PROCESSED_DIR /
            f"{statement_type}s.csv"
        )

        combined_df.to_csv(
            output_file,
            index=False
        )

        print(
            f"\nSaved: {output_file.name}"
        )

        print(
            f"Rows: {len(combined_df):,}"
        )

        print(
            f"Columns: {len(combined_df.columns)}"
        )

    print("\n" + "=" * 60)
    print("CLEANING COMPLETE")
    print("=" * 60)


# --------------------------------------------------
# 7. Run
# --------------------------------------------------

if __name__ == "__main__":
    main()