
SELECT
    p."InvoiceNo" AS original_invoice,
    p."InvoiceDate" AS original_date,
    p."CustomerID",
    p."StockCode",
    p."Description",
    p."Quantity" AS original_quantity,
    p."UnitPrice",
    p."Quantity" * p."UnitPrice" AS original_value,
    c."InvoiceNo" AS cancellation_invoice,
    c."InvoiceDate" AS cancellation_date
FROM retail_transactions p
JOIN retail_transactions c
    ON c."StockCode" = p."StockCode"
   AND c."Quantity" = -p."Quantity"
   AND c."UnitPrice" = p."UnitPrice"
   AND c."InvoiceDate" > p."InvoiceDate"
   AND c.is_cancelled_invoice = TRUE
WHERE p.is_cancelled_invoice = FALSE
  AND p."Quantity" > 0
  AND p."UnitPrice" > 0
ORDER BY p."InvoiceDate"
LIMIT 100;
