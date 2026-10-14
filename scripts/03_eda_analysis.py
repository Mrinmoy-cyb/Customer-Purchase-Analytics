from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_online_retail.csv"
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


# --------------------------------------------------
# 2. Load cleaned data
# --------------------------------------------------

df = pd.read_csv(
    DATA_FILE,
    parse_dates=["InvoiceDate"],
    dtype={"InvoiceNo": "string", 
           "StockCode": "string"},
)

df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")

print("\n========== DATA OVERVIEW ==========")
print(f"Rows: {len(df):,}")
print(f"Unique invoices: {df['InvoiceNo'].nunique():,}")
print(f"Unique products: {df['StockCode'].nunique():,}")
print(f"Identified customers: {df['CustomerID'].nunique():,}")
print(
    "Date range:",
    df["InvoiceDate"].min(),
    "to",
    df["InvoiceDate"].max(),
)


# --------------------------------------------------
# 3. Define an initial sales-analysis population
# --------------------------------------------------
# Positive, priced transaction lines on invoices not
# marked as cancelled. This is an analytical definition,
# not a final accounting measure.

sales = df.loc[
    (~df["is_cancelled_invoice"].astype(bool))
    & (df["Quantity"] > 0)
    & (df["UnitPrice"] > 0)
    & (df["InvoiceDate"].notna())
].copy()

sales["Revenue"] = sales["Quantity"] * sales["UnitPrice"]
sales["Month"] = sales["InvoiceDate"].dt.to_period("M").astype(str)

print("\n========== INITIAL SALES ANALYSIS ==========")
print(f"Eligible transaction lines: {len(sales):,}")
print(f"Revenue: {sales['Revenue'].sum():,.2f}")
print(f"Unique invoices: {sales['InvoiceNo'].nunique():,}")
print(f"Identified customers: {sales['CustomerID'].nunique():,}")


# --------------------------------------------------
# 4. Data-quality summary
# --------------------------------------------------

quality = pd.DataFrame({
    "Metric": [
        "All cleaned rows",
        "Cancellation invoice rows",
        "Negative quantity rows",
        "Zero or negative price rows",
        "Rows missing CustomerID",
        "Rows missing description",
        "Rows eligible for initial sales analysis",
    ],
    "Count": [
        len(df),
        int(df["is_cancelled_invoice"].astype(bool).sum()),
        int((df["Quantity"] < 0).sum()),
        int((df["UnitPrice"] <= 0).sum()),
        int(df["CustomerID"].isna().sum()),
        int(df["Description"].isna().sum()),
        len(sales),
    ],
})

quality.to_csv(REPORT_DIR / "eda_data_quality.csv", index=False)
print("\n========== DATA QUALITY ==========")
print(quality.to_string(index=False))


# --------------------------------------------------
# 5. Monthly revenue
# --------------------------------------------------

monthly = (
    sales.groupby("Month", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Customers=("CustomerID", "nunique"),
        UnitsSold=("Quantity", "sum"),
    )
)

monthly.to_csv(REPORT_DIR / "monthly_sales.csv", index=False)

plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly, x="Month", y="Revenue", marker="o")
plt.title("Monthly Sales Revenue")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(REPORT_DIR / "monthly_revenue.png", dpi=150)
plt.close()

print("\n========== MONTHLY REVENUE ==========")
print(monthly.to_string(index=False))


# --------------------------------------------------
# 6. Top 10 countries by revenue
# --------------------------------------------------

country_sales = (
    sales.groupby("Country", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Customers=("CustomerID", "nunique"),
    )
    .sort_values("Revenue", ascending=False)
)

country_sales.to_csv(REPORT_DIR / "country_sales.csv", index=False)

top_countries = country_sales.head(10)

plt.figure(figsize=(12, 6))
sns.barplot(data=top_countries, x="Revenue", y="Country")
plt.title("Top 10 Countries by Sales Revenue")
plt.xlabel("Revenue")
plt.ylabel("Country")
plt.tight_layout()
plt.savefig(REPORT_DIR / "top_countries.png", dpi=150)
plt.close()

print("\n========== TOP 10 COUNTRIES ==========")
print(top_countries.to_string(index=False))


# --------------------------------------------------
# 7. Top 10 products by revenue
# --------------------------------------------------

product_sales = (
    sales.groupby(["StockCode", "Description"], dropna=False, as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        UnitsSold=("Quantity", "sum"),
        Orders=("InvoiceNo", "nunique"),
    )
    .sort_values("Revenue", ascending=False)
)

product_sales.to_csv(REPORT_DIR / "product_sales.csv", index=False)

print("\n========== TOP 10 PRODUCTS BY REVENUE ==========")
print(product_sales.head(10).to_string(index=False))


# --------------------------------------------------
# 8. Customer purchase behaviour
# --------------------------------------------------

identified_sales = sales.dropna(subset=["CustomerID"]).copy()

customer_summary = (
    identified_sales.groupby("CustomerID", as_index=False)
    .agg(
        Orders=("InvoiceNo", "nunique"),
        TotalSpend=("Revenue", "sum"),
        UnitsPurchased=("Quantity", "sum"),
        LastPurchase=("InvoiceDate", "max"),
    )
    .sort_values("TotalSpend", ascending=False)
)

customer_summary.to_csv(
    REPORT_DIR / "customer_summary.csv",
    index=False,
)

print("\n========== TOP 10 CUSTOMERS BY SPEND ==========")
print(customer_summary.head(10).to_string(index=False))

print("\n========== CUSTOMER SUMMARY ==========")
print(f"Identified customers: {len(customer_summary):,}")
print(
    "Repeat purchasers:",
    f"{(customer_summary['Orders'] >= 2).sum():,}",
)
print(
    "One-order customers:",
    f"{(customer_summary['Orders'] == 1).sum():,}",
)


# --------------------------------------------------
# 9. Initial findings for review
# --------------------------------------------------

print("\n========== INITIAL FINDINGS ==========")

if not monthly.empty:
    best_month = monthly.loc[monthly["Revenue"].idxmax()]
    print(
        f"Highest-revenue month: {best_month['Month']} "
        f"({best_month['Revenue']:,.2f})"
    )

if not country_sales.empty:
    best_country = country_sales.iloc[0]
    print(
        f"Highest-revenue country: {best_country['Country']} "
        f"({best_country['Revenue']:,.2f})"
    )

if not product_sales.empty:
    best_product = product_sales.iloc[0]
    print(
        f"Highest-revenue product: {best_product['Description']} "
        f"({best_product['Revenue']:,.2f})"
    )

print(f"\nEDA completed. Reports saved to: {REPORT_DIR}")
