
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "processed" / "cleaned_online_retail.csv"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, parse_dates=["InvoiceDate"], dtype={
    "InvoiceNo": "string",
    "StockCode": "string",
})

df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
df["LineValue"] = df["Quantity"] * df["UnitPrice"]

invoice = df["InvoiceNo"].str.strip()
df["IsCancellation"] = invoice.str.upper().str.startswith("C", na=False)

# Identify common service and adjustment codes.
# Review this classification against your dataset before final reporting.
non_merchandise_codes = {
    "DOT", "POST", "M", "AMAZONFEE", "B",
    "CRUK", "D", "PADS", "BANK CHARGES",
}

code = df["StockCode"].str.strip().str.upper()
description = df["Description"].fillna("").str.strip().str.upper()

service_description = description.str.contains(
    r"POSTAGE|POSTING FEE|AMAZON FEE|BANK CHARGES|"
    r"ADJUST BAD DEBT|CARRIAGE|DOTCOM POSTAGE|"
    r"MANUAL|DISCOUNT",
    regex=True,
    na=False,
)

df["IsNonMerchandise"] = (
    code.isin(non_merchandise_codes) | service_description
)

# Merchandise transactions with valid dates and positive unit prices.
# Keep negative quantities and cancellation lines for signed-value analysis.
merchandise = df.loc[
    (~df["IsNonMerchandise"])
    & (df["UnitPrice"] > 0)
    & (df["InvoiceDate"].notna())
    & (df["Quantity"] != 0)
].copy()

merchandise["Month"] = (
    merchandise["InvoiceDate"].dt.to_period("M").astype(str)
)

# Net signed merchandise value includes cancellation and return values.
monthly_net = (
    merchandise.groupby("Month", as_index=False)
    .agg(
        NetTransactionValue=("LineValue", "sum"),
        TransactionLines=("InvoiceNo", "size"),
    )
)

monthly_net.to_csv(REPORT_DIR / "monthly_net_merchandise.csv", index=False)

# Completed purchase activity: positive quantities on non-cancelled invoices.
purchases = merchandise.loc[
    (~merchandise["IsCancellation"])
    & (merchandise["Quantity"] > 0)
].copy()

purchases["Revenue"] = purchases["Quantity"] * purchases["UnitPrice"]

# Product rankings on completed purchases.
products = (
    purchases.groupby(["StockCode", "Description"], dropna=False, as_index=False)
    .agg(
        GrossPurchaseValue=("Revenue", "sum"),
        UnitsSold=("Quantity", "sum"),
        Orders=("InvoiceNo", "nunique"),
    )
    .sort_values("GrossPurchaseValue", ascending=False)
)

products.to_csv(REPORT_DIR / "refined_product_rankings.csv", index=False)

# Customer metrics based on identifiable completed purchases.
identified = purchases.dropna(subset=["CustomerID"]).copy()

customers = (
    identified.groupby("CustomerID", as_index=False)
    .agg(
        Orders=("InvoiceNo", "nunique"),
        GrossPurchaseValue=("Revenue", "sum"),
        LastPurchase=("InvoiceDate", "max"),
    )
)

customers.to_csv(REPORT_DIR / "refined_customer_summary.csv", index=False)

print("\n========== REFINED ANALYSIS ==========")
print(f"All source rows: {len(df):,}")
print(f"Merchandise transaction lines: {len(merchandise):,}")
print(f"Non-merchandise rows flagged: {df['IsNonMerchandise'].sum():,}")
print(f"Completed merchandise purchase lines: {len(purchases):,}")
print(f"Completed purchase value: £{purchases['Revenue'].sum():,.2f}")
print(f"Signed merchandise transaction value: £{merchandise['LineValue'].sum():,.2f}")
print(f"Identified purchasing customers: {customers['CustomerID'].nunique():,}")
print(f"Repeat purchasers: {(customers['Orders'] >= 2).sum():,}")

print("\nTop 10 merchandise products by completed purchase value:")
print(products.head(10).to_string(index=False))

print("\nMonthly signed merchandise transaction values:")
print(monthly_net.to_string(index=False))

print("\nReports saved to:", REPORT_DIR)
