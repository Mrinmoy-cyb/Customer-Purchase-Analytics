-------RFM SCORES------ 
WITH purchases AS (
    SELECT
        "CustomerID",
        "InvoiceNo",
        "InvoiceDate",
        "Quantity" * "UnitPrice" AS revenue
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
),
customer_rfm AS (
    SELECT
        "CustomerID",
        MAX("InvoiceDate") AS last_purchase_date,
        COUNT(DISTINCT "InvoiceNo") AS frequency,
        SUM(revenue) AS monetary
    FROM purchases
    GROUP BY "CustomerID"
),
rfm_scores AS (
    SELECT
        *,
        NTILE(5) OVER (
            ORDER BY last_purchase_date ASC
        ) AS recency_score,
        NTILE(5) OVER (
            ORDER BY frequency ASC
        ) AS frequency_score,
        NTILE(5) OVER (
            ORDER BY monetary ASC
        ) AS monetary_score
    FROM customer_rfm
),
segments AS (
    SELECT
        *,
        CASE
            WHEN recency_score >= 4
             AND frequency_score >= 4
             AND monetary_score >= 4
                THEN 'High-value active customers'
            WHEN recency_score >= 3
             AND frequency_score >= 3
                THEN 'Loyal customers'
            WHEN recency_score <= 2
             AND frequency_score >= 3
                THEN 'Previously loyal, inactive'
            WHEN frequency_score <= 2
                THEN 'Occasional customers'
            ELSE 'Other customers'
        END AS customer_segment
    FROM rfm_scores
)
SELECT
    customer_segment,
    COUNT(*) AS customers,
    ROUND(SUM(monetary), 2) AS total_customer_spend,
    ROUND(AVG(monetary), 2) AS average_customer_spend
FROM segments
GROUP BY customer_segment
ORDER BY customers DESC;
