
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_online_retail.csv"
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(
    DATA_FILE,
    dtype={"InvoiceNo": "string", "StockCode": "string"},
    parse_dates=["InvoiceDate"],
)

df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
df["LineValue"] = df["Quantity"] * df["UnitPrice"]

invoice = df["InvoiceNo"].str.strip()
df["IsCancellation"] = invoice.str.upper().str.startswith("C", na=False)

# 1. Compare ordinary invoices and cancellation invoices
print("\n========== INVOICE VALIDATION ==========")

invoice_summary = df.groupby("IsCancellation").agg(
    Lines=("InvoiceNo", "size"),
    Invoices=("InvoiceNo", "nunique"),
    SignedValue=("LineValue", "sum"),
    NegativeQuantityLines=("Quantity", lambda s: (s < 0).sum()),
)

print(invoice_summary.to_string())

# 2. Examine the unusually large customer transactions
print("\n========== CUSTOMER 12346 ==========")

customer = df.loc[df["CustomerID"] == 12346].sort_values("InvoiceDate")

columns = [
    "InvoiceNo", "InvoiceDate", "StockCode",
    "Description", "Quantity", "UnitPrice",
    "LineValue", "IsCancellation",
]

if customer.empty:
    print("Customer 12346 not found.")
else:
    print(customer[columns].to_string(index=False))
    customer[columns].to_csv(
        REPORT_DIR / "customer_12346_transactions.csv",
        index=False,
    )

# 3. Investigate the large PAPER CRAFT transaction
print("\n========== PAPER CRAFT, LITTLE BIRDIE ==========")

paper = df.loc[
    df["StockCode"].str.strip().eq("23843")
].sort_values("InvoiceDate")

print(paper[columns].to_string(index=False))
paper[columns].to_csv(
    REPORT_DIR / "paper_craft_transactions.csv",
    index=False,
)

# 4. Inspect the largest absolute transaction lines
print("\n========== LARGEST TRANSACTION LINES ==========")

largest = (
    df.assign(AbsLineValue=df["LineValue"].abs())
    .nlargest(15, "AbsLineValue")
)

print(largest[columns].to_string(index=False))
largest[columns].to_csv(
    REPORT_DIR / "largest_transaction_lines.csv",
    index=False,
)

# 5. Summarize invoice-level signed values
invoice_totals = (
    df.groupby(["InvoiceNo", "IsCancellation"], as_index=False)
    .agg(
        InvoiceDate=("InvoiceDate", "min"),
        CustomerID=("CustomerID", "first"),
        LineCount=("StockCode", "size"),
        TotalQuantity=("Quantity", "sum"),
        SignedValue=("LineValue", "sum"),
    )
    .sort_values("SignedValue", ascending=False)
)

invoice_totals.to_csv(
    REPORT_DIR / "invoice_validation.csv",
    index=False,
)

print("\nSaved validation reports to:", REPORT_DIR)
print("Transaction validation completed.")
