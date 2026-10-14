
WITH known_reversals AS (
    SELECT
        p."InvoiceNo" AS original_invoice,
        p."CustomerID",
        p."StockCode",
        p."Description",
        p."Quantity" * p."UnitPrice" AS original_value,
        c."InvoiceNo" AS cancellation_invoice,
        c."Quantity" * c."UnitPrice" AS cancellation_value
    FROM retail_transactions p
    JOIN retail_transactions c
      ON c."StockCode" = p."StockCode"
     AND c."Quantity" = -p."Quantity"
     AND c."UnitPrice" = p."UnitPrice"
     AND c."InvoiceDate" > p."InvoiceDate"
     AND c.is_cancelled_invoice = TRUE
    WHERE p."InvoiceNo" IN ('541431', '581483')
      AND p.is_cancelled_invoice = FALSE
)
SELECT
    original_invoice,
    cancellation_invoice,
    "CustomerID",
    "StockCode",
    "Description",
    original_value,
    cancellation_value,
    original_value + cancellation_value AS net_value
FROM known_reversals
ORDER BY original_invoice;
