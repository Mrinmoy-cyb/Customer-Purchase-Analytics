from pathlib import Path
import json
import pandas as pd

# --------------------------------------------------
# 1. Define project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_FILE = RAW_DIR / "Online Retail.xlsx"
OUTPUT_FILE = PROCESSED_DIR / "cleaned_online_retail.csv"
AUDIT_FILE = PROCESSED_DIR / "cleaning_audit.json"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load original dataset
# --------------------------------------------------

print("Loading original dataset...")
df = pd.read_excel(INPUT_FILE)

original_rows = len(df)

print(f"Original rows: {original_rows:,}")


# --------------------------------------------------
# 3. Standardize column data types
# --------------------------------------------------

df["InvoiceNo"] = df["InvoiceNo"].astype("string").str.strip()
df["StockCode"] = df["StockCode"].astype("string").str.strip()
df["Description"] = df["Description"].astype("string").str.strip()
df["Country"] = df["Country"].astype("string").str.strip()

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)

# Customer IDs are identifiers, not continuous numeric values.
df["CustomerID"] = df["CustomerID"].astype("Int64")


# --------------------------------------------------
# 4. Remove exact duplicate rows
# --------------------------------------------------

duplicate_count = int(df.duplicated().sum())

df = df.drop_duplicates().copy()

print(f"Exact duplicate rows removed: {duplicate_count:,}")


# --------------------------------------------------
# 5. Create data-quality flags
# --------------------------------------------------

df["is_cancelled_invoice"] = (
    df["InvoiceNo"]
    .str.upper()
    .str.startswith("C", na=False)
)

df["is_negative_quantity"] = df["Quantity"] < 0

df["is_invalid_price"] = df["UnitPrice"] <= 0

df["has_customer_id"] = df["CustomerID"].notna()

df["has_description"] = (
    df["Description"].notna()
    & df["Description"].str.strip().ne("").fillna(False)
)

df["has_valid_date"] = df["InvoiceDate"].notna()


# --------------------------------------------------
# 6. Create revenue feature
# --------------------------------------------------

# Signed transaction value: negative quantities or prices
# remain visible and are not silently discarded.
df["Revenue"] = df["Quantity"] * df["UnitPrice"]


# --------------------------------------------------
# 7. Generate cleaning audit
# --------------------------------------------------

audit = {
    "original_rows": int(original_rows),
    "duplicate_rows_removed": duplicate_count,
    "rows_after_deduplication": int(len(df)),
    "missing_customer_id": int(df["CustomerID"].isna().sum()),
    "missing_description": int(
        (~df["has_description"]).sum()
    ),
    "cancelled_invoice_rows": int(
        df["is_cancelled_invoice"].sum()
    ),
    "negative_quantity_rows": int(
        df["is_negative_quantity"].sum()
    ),
    "zero_or_negative_price_rows": int(
        df["is_invalid_price"].sum()
    ),
    "invalid_date_rows": int(
        (~df["has_valid_date"]).sum()
    ),
    "revenue_total_including_flagged_rows": round(
        float(df["Revenue"].sum()), 2
    ),
}

# --------------------------------------------------
# 8. Save cleaned dataset and audit report
# --------------------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

with open(AUDIT_FILE, "w", encoding="utf-8") as file:
    json.dump(audit, file, indent=4)

print("\n========== CLEANING SUMMARY ==========")

for key, value in audit.items():
    print(f"{key}: {value}")

print("\nSaved cleaned dataset:")
print(OUTPUT_FILE)

print("\nSaved cleaning audit:")
print(AUDIT_FILE)

print("\nData cleaning and feature engineering completed.")
