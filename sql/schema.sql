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

CREATE INDEX IF NOT EXISTS idx_retail_invoice
    ON retail_transactions ("InvoiceNo");

CREATE INDEX IF NOT EXISTS idx_retail_customer
    ON retail_transactions ("CustomerID");

CREATE INDEX IF NOT EXISTS idx_retail_date
    ON retail_transactions ("InvoiceDate");

CREATE INDEX IF NOT EXISTS idx_retail_stock_code
    ON retail_transactions ("StockCode");

CREATE INDEX IF NOT EXISTS idx_retail_country
    ON retail_transactions ("Country");
