from pathlib import Path
import getpass
import psycopg2

ROOT = Path(__file__).resolve().parent.parent

CSV_FILE = ROOT / "data" / "processed" / "cleaned_online_retail.csv"

TABLE_DDL = """
CREATE TABLE IF NOT EXISTS retail_transactions (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "InvoiceNo" TEXT,
    "StockCode" TEXT,
    "Description" TEXT,
    "Quantity" INTEGER,
    "InvoiceDate" TIMESTAMP,
    "UnitPrice" NUMERIC(14, 4),
    "CustomerID" BIGINT,
    "Country" TEXT,
    is_cancelled_invoice BOOLEAN,
    is_negative_quantity BOOLEAN,
    is_invalid_price BOOLEAN,
    has_customer_id BOOLEAN,
    has_description BOOLEAN,
    has_valid_date BOOLEAN,
    "Revenue" NUMERIC(16, 4)
);
"""

COPY_SQL = """
COPY retail_transactions (
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
    is_cancelled_invoice,
    is_negative_quantity,
    is_invalid_price,
    has_customer_id,
    has_description,
    has_valid_date,
    "Revenue"
)
FROM STDIN WITH (
    FORMAT CSV,
    HEADER TRUE,
    NULL ''
);
"""

INDEX_SQL = [
    'CREATE INDEX IF NOT EXISTS idx_retail_invoice '
    'ON retail_transactions ("InvoiceNo")',
    'CREATE INDEX IF NOT EXISTS idx_retail_customer '
    'ON retail_transactions ("CustomerID")',
    'CREATE INDEX IF NOT EXISTS idx_retail_date '
    'ON retail_transactions ("InvoiceDate")',
    'CREATE INDEX IF NOT EXISTS idx_retail_stock_code '
    'ON retail_transactions ("StockCode")',
    'CREATE INDEX IF NOT EXISTS idx_retail_country '
    'ON retail_transactions ("Country")',
]


def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_FILE}")

    password = getpass.getpass("PostgreSQL postgres password: ")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="customer_purchase_analytics",
        user="postgres",
        password=password,
    )

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(TABLE_DDL)

                # Make reruns safe: replace existing imported rows.
                cur.execute("TRUNCATE TABLE retail_transactions")

                with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
                    cur.copy_expert(COPY_SQL, file)

                cur.execute(
                    "SELECT COUNT(*) FROM retail_transactions"
                )
                row_count = cur.fetchone()[0]

                for statement in INDEX_SQL:
                    cur.execute(statement)

                cur.execute("ANALYZE retail_transactions")

                cur.execute("""
                    SELECT
                        COUNT(DISTINCT "InvoiceNo"),
                        COUNT(DISTINCT "StockCode"),
                        COUNT(DISTINCT "CustomerID"),
                        MIN("InvoiceDate"),
                        MAX("InvoiceDate")
                    FROM retail_transactions
                """)

                invoice_count, product_count, customer_count, start_date, end_date = (
                    cur.fetchone()
                )

        print("\nPostgreSQL import successful!")
        print(f"Rows loaded: {row_count:,}")
        print(f"Unique invoices: {invoice_count:,}")
        print(f"Unique products: {product_count:,}")
        print(f"Identified customers: {customer_count:,}")
        print(f"First transaction: {start_date}")
        print(f"Last transaction: {end_date}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
