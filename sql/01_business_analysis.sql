-- ============================================================
-- FINANCIAL PERFORMANCE & BUSINESS OPERATIONS ANALYTICS
-- SQL BUSINESS ANALYSIS
-- ============================================================


-- ============================================================
-- 1. Company-level financial performance
-- ============================================================

SELECT
    symbol,
    ROUND(AVG(total_revenue), 2) AS avg_revenue,
    ROUND(AVG(net_income), 2) AS avg_net_income,
    ROUND(AVG(net_profit_margin)::numeric, 2) AS avg_profit_margin
FROM financial_metrics
GROUP BY symbol
ORDER BY avg_revenue DESC;


-- ============================================================
-- 2. Highest reported revenue by company
-- ============================================================

SELECT
    symbol,
    MAX(total_revenue) AS highest_revenue
FROM financial_metrics
GROUP BY symbol
ORDER BY highest_revenue DESC;


-- ============================================================
-- 3. Highest reported net income
-- ============================================================

SELECT
    symbol,
    MAX(net_income) AS highest_net_income
FROM financial_metrics
GROUP BY symbol
ORDER BY highest_net_income DESC;


-- ============================================================
-- 4. Average net profit margin
-- ============================================================

SELECT
    symbol,
    ROUND(AVG(net_profit_margin)::numeric, 2) AS avg_profit_margin
FROM financial_metrics
GROUP BY symbol
ORDER BY avg_profit_margin DESC;


-- ============================================================
-- 5. Average operating margin
-- ============================================================

SELECT
    symbol,
    ROUND(AVG(operating_margin)::numeric, 2) AS avg_operating_margin
FROM financial_metrics
GROUP BY symbol
ORDER BY avg_operating_margin DESC;


-- ============================================================
-- 6. Average ROE and ROA
-- ============================================================

SELECT
    symbol,
    ROUND(AVG(roe)::numeric, 2) AS avg_roe,
    ROUND(AVG(roa)::numeric, 2) AS avg_roa
FROM financial_metrics
GROUP BY symbol
ORDER BY avg_roe DESC;


-- ============================================================
-- 7. Debt exposure and risk category
-- ============================================================

SELECT
    symbol,
    ROUND(AVG(debt_to_asset_ratio)::numeric, 2) AS avg_debt_ratio,
    CASE
        WHEN AVG(debt_to_asset_ratio) >= 50
            THEN 'High Debt Exposure'
        WHEN AVG(debt_to_asset_ratio) >= 30
            THEN 'Moderate Debt Exposure'
        ELSE 'Low Debt Exposure'
    END AS risk_category
FROM financial_metrics
GROUP BY symbol
ORDER BY avg_debt_ratio DESC;


-- ============================================================
-- 8. Free cash flow performance
-- ============================================================

SELECT
    symbol,
    ROUND(AVG(free_cash_flow), 2) AS avg_free_cash_flow,
    MAX(free_cash_flow) AS highest_free_cash_flow
FROM financial_metrics
GROUP BY symbol
ORDER BY avg_free_cash_flow DESC;


-- ============================================================
-- 9. Average revenue growth
-- ============================================================

SELECT
    symbol,
    ROUND(AVG(revenue_growth)::numeric, 2) AS avg_revenue_growth
FROM financial_metrics
WHERE revenue_growth IS NOT NULL
GROUP BY symbol
ORDER BY avg_revenue_growth DESC;


-- ============================================================
-- 10. Average net income growth
-- ============================================================

SELECT
    symbol,
    ROUND(AVG(net_income_growth)::numeric, 2) AS avg_income_growth
FROM financial_metrics
WHERE net_income_growth IS NOT NULL
GROUP BY symbol
ORDER BY avg_income_growth DESC;


-- ============================================================
-- 11. Latest financial performance
-- ============================================================

WITH latest AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY fiscal_date::date DESC
        ) AS rn
    FROM financial_metrics
)

SELECT
    symbol,
    fiscal_date::date AS fiscal_date,
    total_revenue,
    net_income,
    net_profit_margin,
    operating_margin,
    roe,
    roa,
    free_cash_flow
FROM latest
WHERE rn = 1
ORDER BY net_income DESC;


-- ============================================================
-- 12. Year-over-year revenue growth using LAG()
-- ============================================================

WITH revenue_history AS (
    SELECT
        symbol,
        fiscal_date::date AS fiscal_date,
        total_revenue,
        LAG(total_revenue) OVER (
            PARTITION BY symbol
            ORDER BY fiscal_date::date
        ) AS previous_revenue
    FROM financial_metrics
)

SELECT
    symbol,
    fiscal_date,
    total_revenue,
    previous_revenue,
    ROUND(
        (
            (total_revenue - previous_revenue)::numeric
            / NULLIF(previous_revenue, 0)
        ) * 100,
        2
    ) AS revenue_growth
FROM revenue_history
ORDER BY symbol, fiscal_date;


-- ============================================================
-- 13. Latest-year company ranking
-- ============================================================

WITH latest AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY fiscal_date::date DESC
        ) AS rn
    FROM financial_metrics
)

SELECT
    symbol,
    total_revenue,
    net_income,
    net_profit_margin,

    RANK() OVER (
        ORDER BY total_revenue DESC
    ) AS revenue_rank,

    RANK() OVER (
        ORDER BY net_income DESC
    ) AS profit_rank,

    RANK() OVER (
        ORDER BY net_profit_margin DESC
    ) AS margin_rank

FROM latest
WHERE rn = 1
ORDER BY profit_rank;


-- ============================================================
-- 14. Overall financial performance score
-- ============================================================

WITH latest AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY fiscal_date::date DESC
        ) AS rn
    FROM financial_metrics
),

scored AS (
    SELECT
        symbol,
        total_revenue,
        net_income,
        net_profit_margin,
        revenue_growth,
        roe,
        free_cash_flow,

        CASE WHEN net_profit_margin > 15 THEN 1 ELSE 0 END
        +
        CASE WHEN revenue_growth > 10 THEN 1 ELSE 0 END
        +
        CASE WHEN roe > 15 THEN 1 ELSE 0 END
        +
        CASE WHEN free_cash_flow > 0 THEN 1 ELSE 0 END
        AS performance_score

    FROM latest
    WHERE rn = 1
)

SELECT
    symbol,
    total_revenue,
    net_income,
    net_profit_margin,
    revenue_growth,
    roe,
    free_cash_flow,
    performance_score,

    CASE
        WHEN performance_score >= 4 THEN 'Strong'
        WHEN performance_score >= 2 THEN 'Moderate'
        ELSE 'Needs Attention'
    END AS performance_category

FROM scored
ORDER BY performance_score DESC;


-- ============================================================
-- 15. Annual financial trend
-- ============================================================

SELECT
    symbol,
    EXTRACT(YEAR FROM fiscal_date::date) AS fiscal_year,
    total_revenue,
    net_income,
    net_profit_margin,
    operating_margin,
    roe,
    roa,
    free_cash_flow
FROM financial_metrics
ORDER BY symbol, fiscal_year;