-- ============================================================
-- Health Risk Cohort Analysis with Window Functions
-- Segments population by income and analyzes behavioral
-- patterns within each health risk cohort
-- Uses: CTEs, window functions, NTILE, PERCENT_RANK
-- ============================================================

WITH health_cohorts AS (
    SELECT
        state_code,
        income,
        exercise,
        smoking_status,
        bmi_category,
        health_risk_segment,
        general_health,
        COUNT(*) AS cohort_size
    FROM `vitalflow-496409.staging.fact_health_outcomes`
    WHERE health_risk_segment != 'unknown'
        AND income IN ('1', '2')
    GROUP BY
        state_code,
        income,
        exercise,
        smoking_status,
        bmi_category,
        health_risk_segment,
        general_health
),

cohort_summary AS (
    SELECT
        income,
        health_risk_segment,
        SUM(cohort_size) AS total_in_cohort,
        ROUND(
            100.0 * SUM(CASE WHEN exercise = '1' THEN cohort_size ELSE 0 END) /
            NULLIF(SUM(cohort_size), 0),
        2) AS exercise_rate,
        ROUND(
            100.0 * SUM(CASE WHEN smoking_status = '1' THEN cohort_size ELSE 0 END) /
            NULLIF(SUM(cohort_size), 0),
        2) AS smoking_rate
    FROM health_cohorts
    GROUP BY income, health_risk_segment
),

ranked_cohorts AS (
    SELECT
        income,
        health_risk_segment,
        total_in_cohort,
        exercise_rate,
        smoking_rate,
        ROUND(PERCENT_RANK() OVER (
            PARTITION BY health_risk_segment
            ORDER BY exercise_rate
        ) * 100, 2) AS exercise_percentile,
        ROUND(PERCENT_RANK() OVER (
            PARTITION BY health_risk_segment
            ORDER BY smoking_rate DESC
        ) * 100, 2) AS smoking_percentile,
        NTILE(2) OVER (
            PARTITION BY health_risk_segment
            ORDER BY total_in_cohort DESC
        ) AS size_quartile
    FROM cohort_summary
)

SELECT
    income,
    health_risk_segment,
    total_in_cohort,
    exercise_rate,
    smoking_rate,
    exercise_percentile,
    smoking_percentile,
    size_quartile
FROM ranked_cohorts
ORDER BY health_risk_segment, total_in_cohort DESC