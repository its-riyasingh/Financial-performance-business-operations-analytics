import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# File path
BASE_DIR = Path(__file__).resolve().parents[1]

csv_file = (
    BASE_DIR
    / "data"
    / "processed"
    / "financial_metrics.csv"
)


# Load CSV
df = pd.read_csv(csv_file)

print("CSV loaded successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# PostgreSQL connection
engine = create_engine(
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# Load into PostgreSQL
df.to_sql(
    "financial_metrics",
    engine,
    if_exists="replace",
    index=False
)

print("\nData loaded into PostgreSQL successfully!")
print("Table: financial_metrics")