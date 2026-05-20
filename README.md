# VitalFlow 

End-to-end public health & behavior analytics platform built on PySpark, dbt, BigQuery, and Python.

VitalFlow is a full-stack data platform that ingests, transforms, and analyzes 400K+ records from CDC public health surveys and the Stack Overflow Developer Survey. Built to demonstrate production-grade data engineering patterns including PySpark ingestion, dbt dimensional modeling, BigQuery SQL analytics, and a scikit-learn/XGBoost ML layer.

---

## Architecture

Raw Data (CDC BRFSS + Stack Overflow)
             │
             ▼
      PySpark Ingestion
  (fixed-width parsing, schema
   enforcement, column sanitization)
             │
             ▼
    BigQuery — raw layer
  (brfss_2023, stackoverflow_survey)
             │
             ▼
    dbt Transformations
      (staging → marts)
             │
             ▼
   BigQuery — staging layer
  (stg_brfss, stg_stackoverflow,
   fact_health_outcomes,
   fact_survey_responses)
             │
        ┌────┴────┐
        ▼         ▼
  SQL Analytics  Python ML Layer
  (CTEs, window  (XGBoost, SHAP,
   functions,     cross-validation,
   cohort         GridSearchCV)
   analysis)

---

## Tech Stack

| Layer          | Tool                               |
|----------------|------------------------------------|
| Ingestion      | PySpark 3.5.1                      |
| Warehouse      | BigQuery                           |
| Transformation | dbt 1.11                           |
| Analytics      | SQL (BigQuery)                     |
| ML             | Python, XGBoost, scikit-learn, SHAP|
| Version Control| Git / GitHub                       |
| Language       | Python 3.11                        |

---

## Datasets

- **CDC BRFSS 2023** — 433,323 records ([CDC](https://www.cdc.gov/brfss/annual_data/annual_2023.html))
- **Stack Overflow Developer Survey 2023** — 89,184 records ([Kaggle](https://www.kaggle.com/datasets/stackoverflow/stack-overflow-2023-developers-survey))

---

## Project Structure

vitalflow-analytics/
├── ingestion/
│   ├── ingest_brfss.py           # PySpark fixed-width parser for CDC BRFSS data
│   └── ingest_stackoverflow.py   # PySpark CSV ingestion for SO survey data
├── dbt_project/
│   └── vitalflow/
│       ├── models/
│       │   ├── staging/
│       │   │   ├── stg_brfss.sql
│       │   │   ├── stg_stackoverflow.sql
│       │   │   ├── sources.yml
│       │   │   └── schema.yml
│       │   └── marts/
│       │       ├── fact_health_outcomes.sql
│       │       ├── fact_survey_responses.sql
│       │       └── schema.yml
│       └── dbt_project.yml
├── analysis/
│   ├── health_by_profession.sql  # Health risk distribution by income group
│   ├── demographic_trends.sql    # State-level behavioral health trends
│   └── cohort_analysis.sql       # Behavioral cohort analysis with NTILE, PERCENT_RANK
├── ml/
│   ├── health_risk_classifier.py # Random Forest baseline (86.49% accuracy)
│   └── health_risk_xgboost.py    # XGBoost + CV + GridSearch + SHAP (86.62% accuracy)
├── data/
│   └── raw/                      # Raw source data (not committed)
├── .env                          # Environment variables (not committed)
├── gcp-key.json                  # GCP service account key (not committed)
└── README.md

---

### Prerequisites
- Python 3.11
- Java 17 (required for PySpark)
- Google Cloud account with BigQuery enabled
- dbt CLI

---

## Key Findings

- **Income & Health Risk:** Lower income groups show nearly 3x higher rates of high-risk health outcomes compared to higher income groups
- **State Variation:** Puerto Rico (state 72) has the highest high-risk rate at 32.92%; Washington DC (state 11) has the lowest at 13.19% with the highest exercise rate at 84.53%
- **Exercise Impact:** Low-risk cohorts have exercise rates of 81-83% vs 45-47% in high-risk cohorts — a clear behavioral differentiator
- **Developer Workforce:** 89,184 developer survey responses analyzed across employment type, compensation, and tech stack preferences
- **ML Model:** XGBoost binary classifier trained on 308K records achieving 86.62% accuracy on 77K held-out test records, predicting high-risk health outcomes from 9 behavioral features with 5-fold cross-validation (CV mean: 86.52% ± 0.04%)

---

## dbt Models

| Model                   | Type  | Rows    | Description                                       |
|-------------------------|-------|---------|---------------------------------------------------|
| `stg_brfss`             | View  | 433,323 | Staged CDC BRFSS data with renamed columns        |
| `stg_stackoverflow`     | View  | 89,184  | Staged Stack Overflow survey data                 |
| `fact_health_outcomes`  | Table | 432,100 | Health outcomes fact table with risk segmentation |
| `fact_survey_responses` | Table | 89,184  | Developer survey fact table                       |

**Test coverage:** 11/11 tests passing (not_null, unique, accepted_values)

---

## SQL Analytics

| Query                      | Techniques Used                             | Key Insight                                        |
|----------------------------|---------------------------------------------|----------------------------------------------------|
| `health_by_profession.sql` | CTEs, window functions, nested aggregations | Health risk varies significantly by income group   |
| `demographic_trends.sql`   | CTEs, RANK, LAG, PARTITION BY               | State-level health behavior ranking and comparison |
| `cohort_analysis.sql`      | CTEs, NTILE, PERCENT_RANK, window functions | Behavioral patterns within health risk cohorts     |

---

## ML Models

| Model                         | Accuracy | Technique                                    |
|-------------------------------|----------|----------------------------------------------|
| Random Forest (baseline)      | 86.49%   | Binary classification, 9 features            |
| XGBoost + GridSearch + SHAP   | 86.62%   | 5-fold CV, hyperparameter tuning, SHAP values|

---

## License
This project uses publicly available datasets. CDC BRFSS data is public domain. Stack Overflow survey data is licensed under [ODbL](https://opendatacommons.org/licenses/odbl/).