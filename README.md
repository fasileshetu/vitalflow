# VitalFlow 

End-to-end public health & behavior analytics platform built on PySpark, dbt, BigQuery, and Python.

VitalFlow is a full-stack data platform that ingests, transforms, and analyzes 400K+ records from CDC public health surveys and the Stack Overflow Developer Survey. Built to demonstrate production-grade data engineering patterns including PySpark ingestion, dbt dimensional modeling, BigQuery SQL analytics, and a scikit-learn ML layer.

---

## Architecture

Raw Data (CDC BRFSS + Stack Overflow)
        │
        ▼
  PySpark Ingestion
  (schema enforcement, partitioning)
        │
        ▼
  BigQuery — raw layer
        │
        ▼
  dbt Transformations
  (staging → marts)
        │
        ▼
  BigQuery — marts layer
  (fact/dim tables)
        │
        ▼
  SQL Analytics          Python ML Layer
  (cohort analysis,      (scikit-learn
  window functions)       classification)

---

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | PySpark |
| Warehouse | BigQuery |
| Transformation | dbt |
| Analytics | SQL (BigQuery) |
| ML | Python, scikit-learn |
| Version Control | Git / GitHub |

---

## Datasets

| Dataset | Source | Records |
|---|---|---|
| CDC BRFSS 2023 | [CDC](https://www.cdc.gov/brfss/annual_data/annual_2023.html) | 433,323 |
| Stack Overflow Developer Survey 2023 | [Kaggle](https://www.kaggle.com/datasets/stackoverflow/stack-overflow-2023-developers-survey) | 65,000+ |

---

## Project Structure

vitalflow-analytics/
├── ingestion/              # PySpark ingestion scripts
│   ├── ingest_brfss.py
│   └── ingest_stackoverflow.py
├── dbt_project/            # dbt transformation models
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── tests/
│   └── dbt_project.yml
├── analysis/               # SQL analytics queries
│   ├── cohort_analysis.sql
│   ├── health_by_profession.sql
│   └── demographic_trends.sql
├── ml/                     # Python ML layer
│   └── health_risk_classifier.ipynb
├── data/
│   └── raw/                # Raw source data (not committed)
├── .env                    # Environment variables (not committed)
├── gcp-key.json            # GCP service account key (not committed)
└── README.md

---

## Getting Started

### Prerequisites
- Python 3.9+
- Java 8+ (required for PySpark)
- Google Cloud account with BigQuery enabled
- dbt CLI

---

## License

This project uses publicly available datasets. CDC BRFSS data is public domain. Stack Overflow survey data is licensed under [ODbL](https://opendatacommons.org/licenses/odbl/).