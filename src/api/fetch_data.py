import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv


# --------------------------------------------------
# 1. Load API key
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

if not API_KEY:
    raise ValueError(
        "API key not found. Please check your .env file."
    )


# --------------------------------------------------
# 2. Configuration
# --------------------------------------------------

BASE_URL = "https://www.alphavantage.co/query"

COMPANIES = {
    "IBM": "IBM",
    "Microsoft": "MSFT",
    "Apple": "AAPL",
    "Amazon": "AMZN",
    "JPMorgan": "JPM"
}

ENDPOINTS = [
    "INCOME_STATEMENT",
    "BALANCE_SHEET",
    "CASH_FLOW"
]


# --------------------------------------------------
# 3. Raw-data directory
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 4. API request function
# --------------------------------------------------

def fetch_financial_data(symbol, function_name):

    params = {
        "function": function_name,
        "symbol": symbol,
        "apikey": API_KEY
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# 5. Save JSON
# --------------------------------------------------

def save_json(data, company, endpoint):

    filename = f"{company}_{endpoint.lower()}.json"

    filepath = RAW_DIR / filename

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Saved: {filepath}")


# --------------------------------------------------
# 6. Main collection process
# --------------------------------------------------

def main():

    total_requests = len(COMPANIES) * len(ENDPOINTS)

    print("=" * 60)
    print("FINANCIAL DATA COLLECTION")
    print("=" * 60)

    print(f"Companies: {len(COMPANIES)}")
    print(f"Endpoints: {len(ENDPOINTS)}")
    print(f"Total API requests: {total_requests}")
    print("=" * 60)

    successful = 0
    failed = 0

    for company_name, symbol in COMPANIES.items():

        print(f"\nProcessing {company_name} ({symbol})")

        for endpoint in ENDPOINTS:

            print(f"  → Fetching {endpoint}...")

            try:

                data = fetch_financial_data(
                    symbol,
                    endpoint
                )

                # Check for Alpha Vantage error/rate-limit messages
                if "Error Message" in data:
                    print(
                        f"  ❌ API error: "
                        f"{data['Error Message']}"
                    )
                    failed += 1
                    continue

                if "Note" in data:
                    print(
                        f"  ⚠️ API limit/message: "
                        f"{data['Note']}"
                    )
                    failed += 1
                    continue

                save_json(
                    data,
                    symbol,
                    endpoint
                )

                successful += 1

                # Wait between requests
                time.sleep(2)

            except requests.RequestException as error:

                print(
                    f"  ❌ Request failed: {error}"
                )

                failed += 1

    print("\n" + "=" * 60)
    print("COLLECTION COMPLETE")
    print("=" * 60)

    print(f"Successful requests: {successful}")
    print(f"Failed requests: {failed}")
    print(f"Files saved in: {RAW_DIR}")


# --------------------------------------------------
# 7. Run
# --------------------------------------------------

if __name__ == "__main__":
    main()