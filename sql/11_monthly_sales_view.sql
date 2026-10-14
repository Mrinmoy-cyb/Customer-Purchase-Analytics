
CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    DATE_TRUNC('month', "InvoiceDate")::date AS sales_month,

    ROUND(
        SUM(line_value) FILTER (
            WHERE is_reversal_or_return = FALSE
        ), 2
    ) AS positive_purchase_value,

    ROUND(
        SUM(line_value) FILTER (
            WHERE is_reversal_or_return = TRUE
        ), 2
    ) AS reversal_return_value,

    ROUND(SUM(line_value), 2) AS signed_transaction_value,

    COUNT(DISTINCT "InvoiceNo") FILTER (
        WHERE is_cancelled_invoice = FALSE
          AND "Quantity" > 0
          AND "UnitPrice" > 0
    ) AS positive_purchase_invoices,

    COUNT(DISTINCT "CustomerID") FILTER (
        WHERE is_cancelled_invoice = FALSE
          AND "Quantity" > 0
          AND "UnitPrice" > 0
    ) AS purchasing_customers

FROM vw_merchandise_sales
WHERE "InvoiceDate" IS NOT NULL
GROUP BY 1;
