
CREATE OR REPLACE VIEW vw_customer_purchase_summary AS
WITH eligible_purchases AS (
    SELECT *
    FROM vw_merchandise_sales
    WHERE is_cancelled_invoice = FALSE
      AND "Quantity" > 0
      AND "UnitPrice" > 0
      AND "CustomerID" IS NOT NULL
      AND "InvoiceDate" IS NOT NULL
)
SELECT
    "CustomerID",
    COUNT(DISTINCT "InvoiceNo") AS order_count,
    ROUND(
        SUM("Quantity" * "UnitPrice"), 2
    ) AS total_spend,
    SUM("Quantity") AS units_purchased,
    MIN("InvoiceDate") AS first_purchase_date,
    MAX("InvoiceDate") AS last_purchase_date,
    CASE
        WHEN COUNT(DISTINCT "InvoiceNo") = 1
            THEN 'One-time purchaser'
        ELSE 'Repeat purchaser'
    END AS customer_type
FROM eligible_purchases
GROUP BY "CustomerID";
