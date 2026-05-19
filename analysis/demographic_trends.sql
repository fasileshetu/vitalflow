-- ============================================================
-- Behavioral Health Trends by State
-- Analyzes exercise, smoking, and BMI patterns across states
-- Uses: CTEs, window functions, LAG, RANK
-- Key finding: Identifies states with highest health risk
-- behaviors and tracks patterns
-- ============================================================

WITH state_health_behaviors AS (
    SELECT
        state_code,
        exercise,
        smoking_status,
        bmi_category,
        health_risk_segment,
        COUNT(*) AS respondent_count
    FROM `vitalflow-496409.staging.fact_health_outcomes`
    WHERE health_risk_segment != 'unknown'
    GROUP BY
        state_code,
        exercise,
        smoking_status,
        bmi_category,
        health_risk_segment
),

state_risk_summary AS (
    SELECT
        state_code,
        SUM(respondent_count) AS total_respondents,
        SUM(CASE WHEN health_risk_segment = 'high_risk' THEN respondent_count ELSE 0 END) AS high_risk_count,
        SUM(CASE WHEN health_risk_segment = 'medium_risk' THEN respondent_count ELSE 0 END) AS medium_risk_count,
        SUM(CASE WHEN health_risk_segment = 'low_risk' THEN respondent_count ELSE 0 END) AS low_risk_count,
        SUM(CASE WHEN exercise = '1' THEN respondent_count ELSE 0 END) AS exercised_count,
        SUM(CASE WHEN smoking_status = '1' THEN respondent_count ELSE 0 END) AS smoker_count
    FROM state_health_behaviors
    GROUP BY state_code
),

state_metrics AS (
    SELECT
        state_code,
        total_respondents,
        high_risk_count,
        ROUND(100.0 * high_risk_count / total_respondents, 2) AS high_risk_pct,
        ROUND(100.0 * exercised_count / total_respondents, 2) AS exercise_pct,
        ROUND(100.0 * smoker_count / total_respondents, 2) AS smoker_pct
    FROM state_risk_summary
    WHERE total_respondents > 100
)

SELECT
    state_code,
    total_respondents,
    high_risk_pct,
    exercise_pct,
    smoker_pct,
    RANK() OVER (ORDER BY high_risk_pct DESC) AS high_risk_rank,
    RANK() OVER (ORDER BY exercise_pct DESC) AS exercise_rank,
    LAG(high_risk_pct) OVER (ORDER BY state_code) AS prev_state_high_risk_pct,
    ROUND(high_risk_pct - LAG(high_risk_pct) OVER (ORDER BY state_code), 2) AS diff_from_prev_state
FROM state_metrics
ORDER BY high_risk_rank