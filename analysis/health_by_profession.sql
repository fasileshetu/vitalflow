-- ============================================================
-- Health Risk Distribution by Income Group
-- Shows how health risk segments vary across income brackets
-- Uses: CTEs, window functions, nested aggregations
-- Key finding: Lower income groups have significantly higher
-- rates of high-risk health outcomes
-- ============================================================

WITH health_risk_distribution AS (
    SELECT
        health_risk_segment,
        income,
        education,
        COUNT(*) AS total_respondents,
        ROUND(
            100.0 * COUNT(*) /
            SUM(COUNT(*)) OVER (PARTITION BY income),
        2) AS pct_within_income_group
    FROM `vitalflow-496409.staging.fact_health_outcomes`
    WHERE health_risk_segment != 'unknown'
    GROUP BY health_risk_segment, income, education
)

SELECT
    income,
    health_risk_segment,
    SUM(total_respondents) AS total_respondents,
    ROUND(AVG(pct_within_income_group), 2) AS avg_pct_within_income,
    ROW_NUMBER() OVER (
        PARTITION BY income
        ORDER BY SUM(total_respondents) DESC
    ) AS rank_within_income_group
FROM health_risk_distribution
GROUP BY income, health_risk_segment
ORDER BY income, rank_within_income_group