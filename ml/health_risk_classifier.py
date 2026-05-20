import os
from dotenv import load_dotenv
from google.cloud import bigquery
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./gcp-key.json"

client = bigquery.Client(project="vitalflow-496409")

# ── 1. Pull data ──────────────────────────────────────────────
print("Pulling data from BigQuery...")

query = """
SELECT
    exercise,
    smoking_status,
    physical_health_days,
    mental_health_days,
    bmi_category,
    age_group,
    education,
    income,
    state_code,
    CASE 
        WHEN health_risk_segment = 'high_risk' THEN 1 
        ELSE 0 
    END as is_high_risk
FROM `vitalflow-496409.staging.fact_health_outcomes`
WHERE health_risk_segment != 'unknown'
    AND exercise != ' '
    AND smoking_status != ' '
    AND physical_health_days != '  '
    AND mental_health_days != '  '
    AND bmi_category != ' '
    AND age_group != '  '
    AND education != ' '
    AND income != '  '
"""

df = client.query(query).to_dataframe()
print(f"Records pulled: {len(df)}")

# ── 2. Feature engineering ────────────────────────────────────
print("\nEngineering features...")

df["exercise_num"]        = pd.to_numeric(df["exercise"], errors="coerce")
df["smoking_num"]         = pd.to_numeric(df["smoking_status"], errors="coerce")
df["physical_health_num"] = pd.to_numeric(df["physical_health_days"], errors="coerce")
df["mental_health_num"]   = pd.to_numeric(df["mental_health_days"], errors="coerce")
df["bmi_num"]             = pd.to_numeric(df["bmi_category"], errors="coerce")
df["age_num"]             = pd.to_numeric(df["age_group"], errors="coerce")
df["education_num"]       = pd.to_numeric(df["education"], errors="coerce")
df["income_num"]          = pd.to_numeric(df["income"], errors="coerce")
df["state_num"]           = pd.to_numeric(df["state_code"], errors="coerce")

features = [
    "exercise_num",
    "smoking_num",
    "physical_health_num",
    "mental_health_num",
    "bmi_num",
    "age_num",
    "education_num",
    "income_num",
    "state_num"
]

feature_names = [
    "Exercise",
    "Smoking Status",
    "Physical Health Days",
    "Mental Health Days",
    "BMI Category",
    "Age Group",
    "Education",
    "Income",
    "State"
]

df_clean = df.dropna(subset=features)
print(f"Records after cleaning: {len(df_clean)}")

X = df_clean[features]
y = df_clean["is_high_risk"]

# ── 3. Train/test split ───────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain size: {len(X_train)}")
print(f"Test size:  {len(X_test)}")

# ── 4. Train model ────────────────────────────────────────────
print("\nTraining Random Forest classifier...")

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# ── 5. Evaluate ───────────────────────────────────────────────
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ── 6. Confusion matrix ───────────────────────────────────────
cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["not_high_risk", "high_risk"],
    yticklabels=["not_high_risk", "high_risk"]
)
plt.title("VitalFlow — Health Risk Classifier Confusion Matrix")
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.tight_layout()
plt.savefig("ml/confusion_matrix.png", dpi=150)
print("\nConfusion matrix saved to ml/confusion_matrix.png")

# ── 7. Feature importance ─────────────────────────────────────
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]

plt.figure(figsize=(8, 5))
plt.bar(range(len(features)), importances[indices], color="steelblue")
plt.xticks(range(len(features)), [feature_names[i] for i in indices], rotation=15)
plt.title("VitalFlow — Feature Importance")
plt.ylabel("Importance Score")
plt.tight_layout()
plt.savefig("ml/feature_importance.png", dpi=150)
print("Feature importance chart saved to ml/feature_importance.png")

print("\nDone.")