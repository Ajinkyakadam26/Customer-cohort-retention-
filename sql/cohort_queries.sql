-- ClearLend Cohort & Retention Analytics
-- DuckDB | customers.csv

-- 1. Cohort Retention Matrix
WITH cohort_base AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', CAST(acquisition_date AS DATE)) AS cohort_month,
        CAST(acquisition_date AS DATE) AS acq_date,
        CASE 
            WHEN churn_date IS NULL OR churn_date = 'None' THEN NULL
            ELSE CAST(churn_date AS DATE)
        END AS churn_dt
    FROM customers
),
retention_calc AS (
    SELECT
        cohort_month,
        COUNT(*) AS cohort_size,
        SUM(CASE WHEN churn_dt IS NULL OR churn_dt > acq_date + INTERVAL '30' DAY THEN 1 ELSE 0 END) AS ret_30d,
        SUM(CASE WHEN churn_dt IS NULL OR churn_dt > acq_date + INTERVAL '60' DAY THEN 1 ELSE 0 END) AS ret_60d,
        SUM(CASE WHEN churn_dt IS NULL OR churn_dt > acq_date + INTERVAL '90' DAY THEN 1 ELSE 0 END) AS ret_90d,
        SUM(CASE WHEN churn_dt IS NULL OR churn_dt > acq_date + INTERVAL '180' DAY THEN 1 ELSE 0 END) AS ret_180d,
        SUM(CASE WHEN churn_dt IS NULL OR churn_dt > acq_date + INTERVAL '365' DAY THEN 1 ELSE 0 END) AS ret_365d
    FROM cohort_base
    GROUP BY cohort_month
)
SELECT
    cohort_month,
    cohort_size,
    ROUND(ret_30d  * 100.0 / cohort_size, 1) AS pct_30d,
    ROUND(ret_60d  * 100.0 / cohort_size, 1) AS pct_60d,
    ROUND(ret_90d  * 100.0 / cohort_size, 1) AS pct_90d,
    ROUND(ret_180d * 100.0 / cohort_size, 1) AS pct_180d,
    ROUND(ret_365d * 100.0 / cohort_size, 1) AS pct_365d
FROM retention_calc
ORDER BY cohort_month;


-- 2. Churn Rate by Cohort Month
SELECT
    DATE_TRUNC('month', CAST(acquisition_date AS DATE)) AS cohort_month,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN is_active = 'False' OR is_active = FALSE THEN 1 ELSE 0 END) AS churned,
    ROUND(SUM(CASE WHEN is_active = 'False' OR is_active = FALSE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS churn_rate_pct,
    ROUND(SUM(CASE WHEN is_active = 'True' OR is_active = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS retention_rate_pct
FROM customers
GROUP BY cohort_month
ORDER BY cohort_month;


-- 3. LTV by Acquisition Channel
SELECT
    acquisition_channel,
    COUNT(*) AS total_customers,
    ROUND(AVG(ltv), 2) AS avg_ltv,
    ROUND(MIN(ltv), 2) AS min_ltv,
    ROUND(MAX(ltv), 2) AS max_ltv,
    ROUND(MEDIAN(ltv), 2) AS median_ltv,
    ROUND(SUM(ltv), 2) AS total_ltv,
    ROUND(SUM(CASE WHEN is_active = 'True' OR is_active = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS retention_pct
FROM customers
GROUP BY acquisition_channel
ORDER BY avg_ltv DESC;


-- 4. Monthly Active Users Trend
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', CAST(acquisition_date AS DATE)) AS month,
        COUNT(DISTINCT customer_id) AS new_customers,
        SUM(CASE WHEN is_active = 'True' OR is_active = TRUE THEN 1 ELSE 0 END) AS active_customers
    FROM customers
    GROUP BY month
)
SELECT
    month,
    new_customers,
    active_customers,
    SUM(new_customers) OVER (ORDER BY month) AS cumulative_customers
FROM monthly
ORDER BY month;


-- 5. High Churn Risk Customers (active but 0 recent transactions)
SELECT
    customer_id,
    acquisition_channel,
    product,
    region,
    age_group,
    CAST(acquisition_date AS DATE) AS acquisition_date,
    ROUND(ltv, 2) AS ltv,
    ltv_segment,
    loan_amount
FROM customers
WHERE (is_active = 'True' OR is_active = TRUE)
  AND churn_risk = 'True'
ORDER BY ltv DESC
LIMIT 100;


-- 6. LTV Segmentation by Channel and Product
SELECT
    ltv_segment,
    acquisition_channel,
    product,
    COUNT(*) AS customer_count,
    ROUND(AVG(ltv), 2) AS avg_ltv,
    ROUND(AVG(loan_amount), 2) AS avg_loan_amount,
    ROUND(SUM(CASE WHEN is_active = 'True' OR is_active = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS retention_pct
FROM customers
GROUP BY ltv_segment, acquisition_channel, product
ORDER BY
    CASE ltv_segment WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
    avg_ltv DESC;
