"""
Predictive Maintenance Modeling with Automated Decision Support (Google Colab)

Business goals:
1) Predict machine failure risk
2) Identify high-risk machines
3) Support maintenance planning
4) Automate alerting for maintenance teams
5) Translate model outputs into business insights
"""

# ==============================
# Step 1 — Import Libraries
# ==============================
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier


# Plot style for business reporting
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (10, 6)


# ==============================
# Step 2 — Load Dataset
# ==============================
file_path = "cleaned_predictive_maintenance.csv"
df = pd.read_csv(file_path)

if "datetime" in df.columns:
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

print("Dataset loaded.")
print("Shape:", df.shape)
print(df.head())


# ==============================
# Step 3 — Data Preparation
# ==============================
# Target variable required by the project specification.
TARGET = "has_failure"
if TARGET not in df.columns:
    raise ValueError("Target column 'has_failure' not found in dataset.")

# Ensure binary target format.
df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce").fillna(0).astype(int)

# Time features for modeling value extraction.
if "datetime" in df.columns:
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["day"] = df["datetime"].dt.day
    df["hour"] = df["datetime"].dt.hour
    df["dayofweek"] = df["datetime"].dt.dayofweek

# Drop raw datetime from model features (tree model uses engineered time fields).
feature_df = df.drop(columns=[TARGET]).copy()
if "datetime" in feature_df.columns:
    feature_df = feature_df.drop(columns=["datetime"])

# Keep machineID for downstream business interpretation, but exclude it from training features
# to reduce pure identifier leakage risk.
business_machine_id = df["machineID"] if "machineID" in df.columns else pd.Series(np.arange(len(df)), name="machineID")
if "machineID" in feature_df.columns:
    model_X = feature_df.drop(columns=["machineID"])
else:
    model_X = feature_df.copy()

y = df[TARGET]

# Detect feature types.
numeric_features = model_X.select_dtypes(include=[np.number]).columns.tolist()
categorical_features = model_X.select_dtypes(exclude=[np.number]).columns.tolist()

# Preprocessing:
# - Numeric: median impute + scaling (scaling is optional for RF, but included for pipeline portability)
# - Categorical: most-frequent impute + one-hot encoding
numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

# Train-test split with stratification for class balance preservation.
X_train, X_test, y_train, y_test = train_test_split(
    model_X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


# ==============================
# Step 4 — Model Development
# ==============================
rf_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced_subsample",
    n_jobs=-1,
)

clf = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", rf_model),
    ]
)

clf.fit(X_train, y_train)

# Predictions and probabilities on test set
y_pred = clf.predict(X_test)
y_proba = clf.predict_proba(X_test)[:, 1]

# Evaluation metrics
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
roc_auc = roc_auc_score(y_test, y_proba)

print("\n=== Model Performance (Random Forest) ===")
print(f"Accuracy : {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall   : {rec:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC AUC  : {roc_auc:.4f}")

# Metric interpretation comments:
# - Accuracy: overall correctness, but can be misleading in imbalanced failure datasets.
# - Precision: among predicted failures, how many are true failures (cost of false alarms).
# - Recall: among actual failures, how many are caught (critical for downtime prevention).
# - F1: balance between precision and recall.
# - ROC AUC: ranking quality of predicted failure probabilities.


# ==============================
# Step 5 — Failure Probability
# ==============================
all_proba = clf.predict_proba(model_X)[:, 1]
df["failure_probability"] = all_proba


# ==============================
# Step 6 — Risk Segmentation
# ==============================
df["risk_level"] = np.select(
    [df["failure_probability"] < 0.4, df["failure_probability"].between(0.4, 0.7, inclusive="both")],
    ["Low Risk", "Medium Risk"],
    default="High Risk",
)

print("\nRisk distribution:")
print(df["risk_level"].value_counts(dropna=False))


# ==============================
# Step 7 — Business Interpretation
# ==============================
# Feature importance extraction from pipeline.
preprocessor_fitted = clf.named_steps["preprocessor"]
model_fitted = clf.named_steps["model"]

feature_names = preprocessor_fitted.get_feature_names_out()
importances = model_fitted.feature_importances_
importance_df = pd.DataFrame({"feature": feature_names, "importance": importances}).sort_values(
    "importance", ascending=False
)

print("\nTop 15 feature importance drivers:")
print(importance_df.head(15))

# High-risk machines summary (aggregate by machine)
if "machineID" in df.columns:
    risk_machine_summary = (
        pd.DataFrame(
            {
                "machineID": business_machine_id,
                "failure_probability": df["failure_probability"],
                "risk_level": df["risk_level"],
                "has_failure": df[TARGET],
            }
        )
        .groupby("machineID", as_index=False)
        .agg(
            max_failure_probability=("failure_probability", "max"),
            avg_failure_probability=("failure_probability", "mean"),
            latest_risk_level=("risk_level", "last"),
            historical_failures=("has_failure", "sum"),
        )
        .sort_values("max_failure_probability", ascending=False)
    )
else:
    risk_machine_summary = pd.DataFrame()

print("\nTop 10 high-risk machines:")
print(risk_machine_summary.head(10))

print("\nBusiness Recommendations:")
print("1) Prioritize inspection for machines with highest max_failure_probability (>0.7).")
print("2) Use top feature drivers to design targeted preventive maintenance tasks.")
print("3) Schedule preemptive checks for Medium Risk assets before they shift to High Risk.")
print("4) Combine model alerts with maintenance history to reduce unnecessary interventions.")


# ==============================
# Step 8 — Automation Alert System
# ==============================
def send_maintenance_alerts(
    high_risk_df: pd.DataFrame,
    sender_email: str = "your_email@example.com",
    sender_password: str = "your_app_password",
    recipient_email: str = "maintenance_team@example.com",
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587,
    send_email: bool = False,
):
    """
    Send automated email alert when any machine has probability > 0.7.

    By default send_email=False for safe Colab demonstration.
    Set send_email=True and valid credentials to activate real sending.
    """

    if high_risk_df.empty:
        print("No high-risk machines detected. No alert sent.")
        return

    lines = [
        "Automated Predictive Maintenance Alert",
        "",
        "The following machines are classified as HIGH RISK (failure probability > 0.7):",
    ]

    for _, row in high_risk_df.iterrows():
        machine_id = row.get("machineID", "Unknown")
        probability = row.get("failure_probability", np.nan)
        risk_level = row.get("risk_level", "High Risk")
        recommendation = "Immediate inspection and preventive maintenance within 24 hours."
        lines.append(
            f"- Machine ID: {machine_id} | Probability: {probability:.3f} | "
            f"Risk: {risk_level} | Recommendation: {recommendation}"
        )

    message_body = "\n".join(lines)

    if not send_email:
        print("\n[DRY RUN] Email alert content prepared (not sent):\n")
        print(message_body)
        return

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = "High-Risk Machine Alert - Predictive Maintenance"
    msg.attach(MIMEText(message_body, "plain"))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()

    print(f"Alert email sent to {recipient_email}.")


# Trigger alert condition
alert_df = df[df["failure_probability"] > 0.7][["machineID", "failure_probability", "risk_level"]].drop_duplicates()
send_maintenance_alerts(alert_df, send_email=False)


# ==============================
# Step 9 — Visual Output
# ==============================
# 1) Feature Importance Chart
plt.figure(figsize=(12, 7))
plot_imp = importance_df.head(15).sort_values("importance", ascending=True)
plt.barh(plot_imp["feature"], plot_imp["importance"], color="#4C72B0")
plt.title("Top 15 Feature Importances (Random Forest)")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()

# 2) Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
fig, ax = plt.subplots(figsize=(6, 5))
disp.plot(ax=ax, cmap="Blues", values_format="d")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.show()

# 3) ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_proba)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f"Random Forest (AUC = {roc_auc:.3f})", color="#C44E52")
plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random baseline")
plt.title("ROC Curve")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend(loc="lower right")
plt.tight_layout()
plt.show()


# ==============================
# Step 10 — Save Outputs / Goal
# ==============================
scored_output = "predictive_maintenance_scored.csv"
df.to_csv(scored_output, index=False)
print(f"\nScored dataset saved as: {scored_output}")

if not risk_machine_summary.empty:
    risk_machine_summary.to_csv("high_risk_machine_summary.csv", index=False)
    print("High-risk machine summary saved as: high_risk_machine_summary.csv")

print(
    "\nCompleted: Predictive analytics + decision support + automation integration ready for business use."
)
