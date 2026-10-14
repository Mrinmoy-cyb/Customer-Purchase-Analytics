--------- QUERY 1- OVERALL SALES KPIS-------

WITH merchandise AS (
    SELECT *
    FROM retail_transactions
    WHERE UPPER(TRIM("StockCode")) NOT IN (
        'DOT', 'POST', 'M', 'AMAZONFEE',
        'B', 'CRUK', 'D', 'PADS', 'BANK CHARGES'
    )
    AND COALESCE(UPPER("Description"), '') !~
        'POSTAGE|POSTING FEE|AMAZON FEE|BANK CHARGES|ADJUST BAD DEBT|CARRIAGE|DOTCOM POSTAGE|MANUAL|DISCOUNT'
),
purchases AS (
    SELECT *
    FROM merchandise
    WHERE is_cancelled_invoice = FALSE
      AND "Quantity" > 0
      AND "UnitPrice" > 0
      AND "InvoiceDate" IS NOT NULL
)
SELECT
    ROUND(SUM("Quantity" * "UnitPrice"), 2)
        AS completed_purchase_value,
    COUNT(DISTINCT "InvoiceNo") AS invoice_count,
    COUNT(DISTINCT "CustomerID") AS identified_customers,
    SUM("Quantity") AS units_sold,
    ROUND(
        SUM("Quantity" * "UnitPrice")
        / NULLIF(COUNT(DISTINCT "InvoiceNo"), 0),
        2
    ) AS average_invoice_value
FROM purchases;


---------Query 2 — Monthly revenue trends--------

WITH purchases AS (
    SELECT *
    FROM retail_transactions
    WHERE is_cancelled_invoice = FALSE
      AND "Quantity" > 0
      AND "UnitPrice" > 0
      AND "InvoiceDate" IS NOT NULL
      AND UPPER(TRIM("StockCode")) NOT IN (
          'DOT', 'POST', 'M', 'AMAZONFEE',
          'B', 'CRUK', 'D', 'PADS', 'BANK CHARGES'
      )
      AND COALESCE(UPPER("Description"), '') !~
          'POSTAGE|POSTING FEE|AMAZON FEE|BANK CHARGES|ADJUST BAD DEBT|CARRIAGE|DOTCOM POSTAGE|MANUAL|DISCOUNT'
)
SELECT
    DATE_TRUNC('month', "InvoiceDate")::date AS sales_month,
    ROUND(SUM("Quantity" * "UnitPrice"), 2) AS revenue,
    COUNT(DISTINCT "InvoiceNo") AS orders,
    COUNT(DISTINCT "CustomerID") AS customers,
    SUM("Quantity") AS units_sold
FROM purchases
GROUP BY 1
ORDER BY 1;


--------Query 3 — Top 10 products by revenue-------

SELECT
    "StockCode",
    "Description",
    ROUND(SUM("Quantity" * "UnitPrice"), 2) AS revenue,
    SUM("Quantity") AS units_sold,
    COUNT(DISTINCT "InvoiceNo") AS orders
FROM retail_transactions
WHERE is_cancelled_invoice = FALSE
  AND "Quantity" > 0
  AND "UnitPrice" > 0
  AND "InvoiceDate" IS NOT NULL
  AND UPPER(TRIM("StockCode")) NOT IN (
      'DOT', 'POST', 'M', 'AMAZONFEE',
      'B', 'CRUK', 'D', 'PADS', 'BANK CHARGES'
  )
  AND COALESCE(UPPER("Description"), '') !~
      'POSTAGE|POSTING FEE|AMAZON FEE|BANK CHARGES|ADJUST BAD DEBT|CARRIAGE|DOTCOM POSTAGE|MANUAL|DISCOUNT'
GROUP BY "StockCode", "Description"
ORDER BY revenue DESC
LIMIT 10;

---------Query 4 — Customer purchase frequency--------------

WITH customer_orders AS (
    SELECT
        "CustomerID",
        COUNT(DISTINCT "InvoiceNo") AS order_count,
        SUM("Quantity" * "UnitPrice") AS total_spend
    FROM retail_transactions
    WHERE "CustomerID" IS NOT NULL
      AND is_cancelled_invoice = FALSE
      AND "Quantity" > 0
      AND "UnitPrice" > 0
      AND "InvoiceDate" IS NOT NULL
      AND UPPER(TRIM("StockCode")) NOT IN (
          'DOT', 'POST', 'M', 'AMAZONFEE',
          'B', 'CRUK', 'D', 'PADS', 'BANK CHARGES'
      )
      AND COALESCE(UPPER("Description"), '') !~
          'POSTAGE|POSTING FEE|AMAZON FEE|BANK CHARGES|ADJUST BAD DEBT|CARRIAGE|DOTCOM POSTAGE|MANUAL|DISCOUNT'
    GROUP BY "CustomerID"
)
SELECT
    CASE
        WHEN order_count = 1 THEN 'One-time purchaser'
        ELSE 'Repeat purchaser'
    END AS customer_type,
    COUNT(*) AS customers,
    ROUND(SUM(total_spend), 2) AS total_spend,
    ROUND(AVG(total_spend), 2) AS average_customer_spend
FROM customer_orders
GROUP BY 1
ORDER BY customers DESC;


----------Query 5 — Top 10 customers by spending---------------

SELECT
    "CustomerID",
    COUNT(DISTINCT "InvoiceNo") AS order_count,
    ROUND(SUM("Quantity" * "UnitPrice"), 2) AS total_spend,
    MAX("InvoiceDate") AS last_purchase_date
FROM retail_transactions
WHERE "CustomerID" IS NOT NULL
  AND is_cancelled_invoice = FALSE
  AND "Quantity" > 0
  AND "UnitPrice" > 0
  AND "InvoiceDate" IS NOT NULL
  AND UPPER(TRIM("StockCode")) NOT IN (
      'DOT', 'POST', 'M', 'AMAZONFEE',
      'B', 'CRUK', 'D', 'PADS', 'BANK CHARGES'
  )
  AND COALESCE(UPPER("Description"), '') !~
      'POSTAGE|POSTING FEE|AMAZON FEE|BANK CHARGES|ADJUST BAD DEBT|CARRIAGE|DOTCOM POSTAGE|MANUAL|DISCOUNT'
GROUP BY "CustomerID"
ORDER BY total_spend DESC
LIMIT 10;