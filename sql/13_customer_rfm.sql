
CREATE OR REPLACE VIEW vw_customer_rfm AS
WITH customer_metrics AS (
    SELECT
        "CustomerID",
        COUNT(DISTINCT "InvoiceNo") AS frequency,
        SUM("Quantity" * "UnitPrice") AS monetary_value,
        MAX("InvoiceDate") AS last_purchase_date
    FROM vw_merchandise_sales
    WHERE is_cancelled_invoice = FALSE
      AND "Quantity" > 0
      AND "UnitPrice" > 0
      AND "CustomerID" IS NOT NULL
      AND "InvoiceDate" IS NOT NULL
    GROUP BY "CustomerID"
),
scored AS (
    SELECT
        *,
        (DATE '2011-12-10' - last_purchase_date::date)
            AS recency_days,
        NTILE(5) OVER (
            ORDER BY last_purchase_date
        ) AS r_score,
        NTILE(5) OVER (
            ORDER BY frequency
        ) AS f_score,
        NTILE(5) OVER (
            ORDER BY monetary_value
        ) AS m_score
    FROM customer_metrics
)

SELECT
    *,
    (6 - r_score) AS recency_score,
    f_score AS frequency_score,
    m_score AS monetary_score,
    CASE
        WHEN r_score >= 4
          AND f_score >= 4
          AND m_score >= 4
            THEN 'Champions'

        WHEN r_score >= 3
          AND f_score >= 3
            THEN 'Loyal Customers'

        WHEN r_score >= 4
          AND f_score <= 2
            THEN 'Recent Customers'

        WHEN r_score <= 2
          AND f_score >= 3
            THEN 'At Risk'

        WHEN r_score <= 2
          AND f_score <= 2
            THEN 'Hibernating'

        ELSE 'Potential Loyalists'
    END AS rfm_segment
FROM scored;
