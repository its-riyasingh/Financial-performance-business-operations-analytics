from pathlib import Path
import pandas as pd

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"

# Load data
income = pd.read_csv(DATA_DIR / "incomes.csv")
balance = pd.read_csv(DATA_DIR / "balances.csv")
cashflow = pd.read_csv(DATA_DIR / "cashflows.csv")

# Keep annual reports
income = income[income["period_type"] == "Annual"]
balance = balance[balance["period_type"] == "Annual"]
cashflow = cashflow[cashflow["period_type"] == "Annual"]

# Convert dates
for df in [income, balance, cashflow]:
    df["fiscalDateEnding"] = pd.to_datetime(df["fiscalDateEnding"])

# Select important financial fields
income = income[
    [
        "symbol", "fiscalDateEnding",
        "totalRevenue", "grossProfit",
        "operatingIncome", "netIncome"
    ]
]

balance = balance[
    [
        "symbol", "fiscalDateEnding",
        "totalAssets", "totalLiabilities",
        "totalShareholderEquity",
        "shortTermDebt", "longTermDebt"
    ]
]

cashflow = cashflow[
    [
        "symbol", "fiscalDateEnding",
        "operatingCashflow",
        "capitalExpenditures"
    ]
]

# Merge statements
df = income.merge(
    balance,
    on=["symbol", "fiscalDateEnding"],
    how="inner"
)

df = df.merge(
    cashflow,
    on=["symbol", "fiscalDateEnding"],
    how="inner"
)

# Feature engineering
df["gross_margin"] = (
    df["grossProfit"] / df["totalRevenue"] * 100
)

df["operating_margin"] = (
    df["operatingIncome"] / df["totalRevenue"] * 100
)

df["net_profit_margin"] = (
    df["netIncome"] / df["totalRevenue"] * 100
)

df["total_debt"] = (
    df["shortTermDebt"].fillna(0)
    + df["longTermDebt"].fillna(0)
)

df["debt_to_asset_ratio"] = (
    df["total_debt"] / df["totalAssets"] * 100
)

df["roe"] = (
    df["netIncome"]
    / df["totalShareholderEquity"]
    * 100
)

df["roa"] = (
    df["netIncome"]
    / df["totalAssets"]
    * 100
)

df["free_cash_flow"] = (
    df["operatingCashflow"]
    - df["capitalExpenditures"]
)

# Growth
df = df.sort_values(["symbol", "fiscalDateEnding"])

df["revenue_growth"] = (
    df.groupby("symbol")["totalRevenue"]
    .pct_change() * 100
)

df["net_income_growth"] = (
    df.groupby("symbol")["netIncome"]
    .pct_change() * 100
)

# Round metrics
# df = df.round(2)
numeric_columns = df.select_dtypes(include="number").columns
df[numeric_columns] = df[numeric_columns].round(2)

# Save
output = DATA_DIR / "financial_metrics.csv"
df.to_csv(output, index=False)

print("Financial feature engineering complete!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Saved to:", output)