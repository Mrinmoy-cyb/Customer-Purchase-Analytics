
CREATE OR REPLACE VIEW vw_merchandise_sales AS
SELECT
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
    "Quantity" * "UnitPrice" AS line_value,
    is_cancelled_invoice,
    CASE
        WHEN is_cancelled_invoice = TRUE
          OR "Quantity" < 0
        THEN TRUE
        ELSE FALSE
    END AS is_reversal_or_return
FROM retail_transactions
WHERE UPPER(TRIM("StockCode")) NOT IN (
    'DOT', 'POST', 'M', 'AMAZONFEE',
    'B', 'CRUK', 'D', 'PADS', 'BANK CHARGES'
)
AND COALESCE(UPPER("Description"), '') !~
    'POSTAGE|POSTING FEE|AMAZON FEE|BANK CHARGES|ADJUST BAD DEBT|CARRIAGE|DOTCOM POSTAGE|MANUAL|DISCOUNT';
