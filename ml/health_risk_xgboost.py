import os
from dotenv import load_dotenv
from google.cloud import bigquery
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import shap

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

# Engineered features
df["bad_health_days_total"] = df["physical_health_num"] + df["mental_health_num"]
df["healthy_behavior"]      = ((df["exercise_num"] == 1) & (df["smoking_num"] == 2)).astype(int)
df["age_bmi_interaction"]   = df["age_num"] * df["bmi_num"]
df["high_bmi"]              = (df["bmi_num"] >= 3).astype(int)
df["senior"]                = (df["age_num"] >= 7).astype(int)
df["low_income"]            = (df["income_num"] <= 3).astype(int)

features = [
    "exercise_num",
    "smoking_num",
    "physical_health_num",
    "mental_health_num",
    "bmi_num",
    "age_num",
    "education_num",
    "income_num",
    "state_num",
    "bad_health_days_total",
    "healthy_behavior",
    "age_bmi_interaction",
    "high_bmi",
    "senior",
    "low_income"
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
    "State",
    "Bad Health Days Total",
    "Healthy Behavior Score",
    "Age x BMI Interaction",
    "High BMI Flag",
    "Senior Flag",
    "Low Income Flag"
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

# ── 4. Cross-validation ───────────────────────────────────────
print("\nRunning 5-fold cross-validation...")

cv_model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss",
    n_jobs=-1
)

cv_scores = cross_val_score(cv_model, X_train, y_train, cv=5, scoring="accuracy")
print(f"CV Scores: {cv_scores.round(4)}")
print(f"CV Mean:   {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# ── 5. Hyperparameter tuning ──────────────────────────────────
print("\nRunning GridSearchCV...")

param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [4, 6, 8],
    "learning_rate": [0.05, 0.1]
}

grid_search = GridSearchCV(
    XGBClassifier(random_state=42, eval_metric="logloss", n_jobs=-1),
    param_grid,
    cv=3,
    scoring="accuracy",
    verbose=1
)

grid_search.fit(X_train, y_train)
print(f"\nBest params: {grid_search.best_params_}")
print(f"Best CV score: {grid_search.best_score_:.4f}")

# ── 6. Train final model ──────────────────────────────────────
print("\nTraining final XGBoost model...")
model = grid_search.best_estimator_
model.fit(X_train, y_train)

# ── 7. Evaluate ───────────────────────────────────────────────
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ── 8. Confusion matrix ───────────────────────────────────────
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
plt.title("VitalFlow — XGBoost Health Risk Classifier Confusion Matrix")
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.tight_layout()
plt.savefig("ml/xgboost_confusion_matrix.png", dpi=150)
print("\nConfusion matrix saved to ml/xgboost_confusion_matrix.png")

# ── 9. SHAP values ────────────────────────────────────────────
print("\nCalculating SHAP values...")

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test[:1000])

plt.figure()
shap.summary_plot(
    shap_values,
    X_test[:1000],
    feature_names=feature_names,
    show=False
)
plt.title("VitalFlow — SHAP Feature Importance")
plt.tight_layout()
plt.savefig("ml/shap_summary.png", dpi=150, bbox_inches="tight")
print("SHAP summary plot saved to ml/shap_summary.png")

print("\nDone.")