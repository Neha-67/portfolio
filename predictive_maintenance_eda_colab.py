"""
Business-Oriented Exploratory Data Analysis (EDA)
for Predictive Maintenance dataset in Google Colab.

Input:
    cleaned_predictive_maintenance.csv

Output:
    - Data quality diagnostics
    - Business-focused charts and summaries
    - Operational insights for maintenance optimization
"""

# ==============================
# Step 1 — Import Libraries
# ==============================
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Optional interactive charts
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except Exception:  # Keep notebook robust even if plotly isn't installed
    PLOTLY_AVAILABLE = False

warnings.filterwarnings("ignore")

# Visual style for executive-friendly charts
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.figsize"] = (12, 6)


# ==============================
# Step 2 — Load Data
# ==============================
file_path = "cleaned_predictive_maintenance.csv"
df = pd.read_csv(file_path)

# Ensure datetime parsed for time-series analysis
if "datetime" in df.columns:
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

print("=== Dataset Shape ===")
print(df.shape)

print("\n=== Head ===")
print(df.head())

print("\n=== Info ===")
print(df.info())

print("\n=== Summary Statistics (Numeric) ===")
print(df.describe().T)

print("\n=== Summary Statistics (Categorical) ===")
print(df.describe(include=["object", "category"]).T)


# ==============================
# Step 3 — Data Quality Check
# ==============================
print("\n=== Missing Value Analysis ===")
missing_counts = df.isna().sum().sort_values(ascending=False)
missing_pct = (missing_counts / len(df) * 100).round(2)
missing_table = pd.DataFrame({"missing_count": missing_counts, "missing_pct": missing_pct})
print(missing_table[missing_table["missing_count"] > 0])

print("\n=== Duplicate Rows ===")
duplicate_rows = df.duplicated().sum()
print(f"Duplicate rows: {duplicate_rows}")

print("\n=== Data Types Verification ===")
print(df.dtypes)

# Missing value visualization
plt.figure(figsize=(14, 6))
missing_table_plot = missing_table.reset_index().rename(columns={"index": "column"})
sns.barplot(data=missing_table_plot, x="column", y="missing_pct", color="#4C72B0")
plt.xticks(rotation=75)
plt.title("Missing Values by Column (%)")
plt.xlabel("Columns")
plt.ylabel("Missing %")
plt.tight_layout()
plt.show()


# ==============================
# Utility / defensive preparation
# ==============================
# Harmonize expected business columns if prior pipeline used a different name.
if "machine_age_category" not in df.columns and "age_category" in df.columns:
    df["machine_age_category"] = df["age_category"]

# Build risk_level if it does not exist using health_score quantiles.
if "risk_level" not in df.columns:
    if "health_score" in df.columns:
        q1 = df["health_score"].quantile(0.33)
        q2 = df["health_score"].quantile(0.66)
        # Lower health score implies higher risk.
        df["risk_level"] = np.select(
            [df["health_score"] <= q1, df["health_score"] <= q2],
            ["High", "Medium"],
            default="Low",
        )
    else:
        df["risk_level"] = "Unknown"

# Ensure binary flags are numeric (0/1) when possible.
for flag_col in ["has_failure", "has_error", "has_maint"]:
    if flag_col in df.columns:
        df[flag_col] = pd.to_numeric(df[flag_col], errors="coerce").fillna(0).astype(int)


# ==============================
# Step 4 — Univariate Analysis
# ==============================
numeric_features = ["volt", "rotate", "pressure", "vibration", "age", "health_score"]
categorical_features = ["model", "machine_age_category", "risk_level", "has_failure", "has_error", "has_maint"]

print("\n=== Univariate Analysis ===")

# Numeric distributions: histogram + boxplot
for col in numeric_features:
    if col in df.columns:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        sns.histplot(df[col].dropna(), kde=True, bins=30, ax=axes[0], color="#4C72B0")
        axes[0].set_title(f"Distribution of {col}")
        axes[0].set_xlabel(col)

        sns.boxplot(x=df[col], ax=axes[1], color="#55A868")
        axes[1].set_title(f"Boxplot of {col}")
        axes[1].set_xlabel(col)

        plt.tight_layout()
        plt.show()

        # Business comment examples:
        # - Wider spread may indicate unstable operation conditions.
        # - Extreme outliers may represent abnormal sensor behavior worth root-cause review.

# Categorical distributions
for col in categorical_features:
    if col in df.columns:
        plt.figure(figsize=(10, 5))
        order = df[col].astype(str).value_counts().index
        sns.countplot(data=df, x=col, order=order, palette="viridis")
        plt.title(f"Count Plot: {col}")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()

        # Business comment examples:
        # - Dominant categories help prioritize resource allocation.
        # - Under-represented classes may affect model learning and KPI interpretation.


# ==============================
# Step 5 — Bivariate Analysis
# ==============================
print("\n=== Bivariate Analysis vs Failure ===")

if "has_failure" in df.columns:
    # Sensor values vs failure
    for col in ["volt", "rotate", "pressure", "vibration", "health_score"]:
        if col in df.columns:
            plt.figure(figsize=(10, 5))
            sns.boxplot(data=df, x="has_failure", y=col, palette="Set2")
            plt.title(f"{col} vs Failure")
            plt.xlabel("has_failure (0=No, 1=Yes)")
            plt.tight_layout()
            plt.show()

    # Age vs failure
    if "age" in df.columns:
        plt.figure(figsize=(10, 5))
        sns.boxplot(data=df, x="has_failure", y="age", palette="coolwarm")
        plt.title("Machine Age vs Failure")
        plt.tight_layout()
        plt.show()

    # Model vs failure rate
    if "model" in df.columns:
        model_failure = (
            df.groupby("model", dropna=False)["has_failure"]
            .mean()
            .sort_values(ascending=False)
            .reset_index(name="failure_rate")
        )
        plt.figure(figsize=(10, 5))
        sns.barplot(data=model_failure, x="model", y="failure_rate", palette="rocket")
        plt.title("Failure Rate by Machine Model")
        plt.ylabel("Failure Rate")
        plt.tight_layout()
        plt.show()

    # Maintenance vs failure
    if "has_maint" in df.columns:
        maint_failure = (
            df.groupby("has_maint")["has_failure"]
            .mean()
            .reset_index(name="failure_rate")
        )
        plt.figure(figsize=(8, 5))
        sns.barplot(data=maint_failure, x="has_maint", y="failure_rate", palette="magma")
        plt.title("Failure Rate by Maintenance Event Presence")
        plt.xlabel("has_maint (0=No, 1=Yes)")
        plt.ylabel("Failure Rate")
        plt.tight_layout()
        plt.show()

    # Group summaries for business review
    summary_cols = [c for c in ["volt", "rotate", "pressure", "vibration", "health_score", "age"] if c in df.columns]
    if summary_cols:
        print("\nGroup Summary (mean by has_failure):")
        print(df.groupby("has_failure")[summary_cols].mean().round(3))


# ==============================
# Step 6 — Correlation Analysis
# ==============================
print("\n=== Correlation Analysis ===")

numeric_df = df.select_dtypes(include=[np.number]).copy()
if not numeric_df.empty:
    corr = numeric_df.corr(numeric_only=True)

    plt.figure(figsize=(14, 10))
    sns.heatmap(corr, cmap="coolwarm", center=0, annot=False)
    plt.title("Correlation Matrix (Numeric Features)")
    plt.tight_layout()
    plt.show()

    if "has_failure" in corr.columns:
        failure_corr = corr["has_failure"].sort_values(ascending=False)
        print("\nCorrelation with has_failure:")
        print(failure_corr)


# ==============================
# Step 7 — Time Series Analysis
# ==============================
print("\n=== Time Series Analysis ===")

if "datetime" in df.columns:
    ts_df = df.dropna(subset=["datetime"]).copy()

    # Failures over time (monthly)
    if "has_failure" in ts_df.columns:
        monthly_failures = (
            ts_df.set_index("datetime")["has_failure"]
            .resample("M")
            .sum()
            .reset_index(name="failures")
        )
        plt.figure(figsize=(12, 5))
        sns.lineplot(data=monthly_failures, x="datetime", y="failures", marker="o", color="#C44E52")
        plt.title("Monthly Failure Counts")
        plt.xlabel("Month")
        plt.ylabel("Failure Count")
        plt.tight_layout()
        plt.show()

    # Maintenance trends over months
    if "has_maint" in ts_df.columns:
        monthly_maint = (
            ts_df.set_index("datetime")["has_maint"]
            .resample("M")
            .sum()
            .reset_index(name="maintenance_events")
        )
        plt.figure(figsize=(12, 5))
        sns.lineplot(data=monthly_maint, x="datetime", y="maintenance_events", marker="o", color="#8172B3")
        plt.title("Monthly Maintenance Events")
        plt.xlabel("Month")
        plt.ylabel("Maintenance Events")
        plt.tight_layout()
        plt.show()

    # Sensor behavior over time (monthly averages)
    sensor_cols = [c for c in ["volt", "rotate", "pressure", "vibration", "health_score"] if c in ts_df.columns]
    if sensor_cols:
        monthly_sensor = ts_df.set_index("datetime")[sensor_cols].resample("M").mean().reset_index()
        plt.figure(figsize=(14, 6))
        for col in sensor_cols:
            plt.plot(monthly_sensor["datetime"], monthly_sensor[col], label=col)
        plt.title("Monthly Average Sensor and Health Trends")
        plt.xlabel("Month")
        plt.ylabel("Average Value")
        plt.legend()
        plt.tight_layout()
        plt.show()


# ==============================
# Step 8 — Risk Segmentation
# ==============================
print("\n=== Risk Segmentation ===")

if "risk_level" in df.columns and "has_failure" in df.columns:
    risk_failure = (
        df.groupby("risk_level", dropna=False)["has_failure"]
        .mean()
        .sort_values(ascending=False)
        .reset_index(name="failure_rate")
    )
    plt.figure(figsize=(8, 5))
    sns.barplot(data=risk_failure, x="risk_level", y="failure_rate", palette="Reds")
    plt.title("Failure Rate by Risk Level")
    plt.tight_layout()
    plt.show()

if "health_score" in df.columns and "has_failure" in df.columns:
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df, x="has_failure", y="health_score", palette="Set3")
    plt.title("Health Score Distribution by Failure Outcome")
    plt.xlabel("has_failure (0=No, 1=Yes)")
    plt.tight_layout()
    plt.show()


# ==============================
# Step 9 — Machine Performance Analysis
# ==============================
print("\n=== Machine Performance Analysis ===")

# Machines with highest failures
if "machineID" in df.columns and "has_failure" in df.columns:
    top_failure_machines = (
        df.groupby("machineID")["has_failure"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index(name="failure_count")
    )
    print("\nTop 10 machines by failure count:")
    print(top_failure_machines)

    plt.figure(figsize=(12, 5))
    sns.barplot(data=top_failure_machines, x="machineID", y="failure_count", palette="flare")
    plt.title("Top 10 Machines by Failure Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Machines with highest risk scores (risk proxy = lowest health score)
if "machineID" in df.columns and "health_score" in df.columns:
    top_risk_machines = (
        df.groupby("machineID")["health_score"]
        .mean()
        .sort_values(ascending=True)
        .head(10)
        .reset_index(name="avg_health_score")
    )
    print("\nTop 10 machines with lowest average health score (highest risk):")
    print(top_risk_machines)

    plt.figure(figsize=(12, 5))
    sns.barplot(data=top_risk_machines, x="machineID", y="avg_health_score", palette="crest")
    plt.title("Top 10 High-Risk Machines (Lowest Avg Health Score)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Models with most issues
if "model" in df.columns and "has_failure" in df.columns:
    model_issues = (
        df.groupby("model", dropna=False)["has_failure"]
        .agg(["sum", "mean", "count"])
        .reset_index()
        .rename(columns={"sum": "failure_count", "mean": "failure_rate", "count": "records"})
        .sort_values("failure_count", ascending=False)
    )
    print("\nModel performance summary:")
    print(model_issues)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=model_issues, x="model", y="failure_count", palette="rocket_r")
    plt.title("Failure Count by Model")
    plt.tight_layout()
    plt.show()


# ==============================
# Step 10 — Insight Extraction
# ==============================
print("\n=== Business-Oriented Insights ===")

insights = []

if "has_failure" in numeric_df.columns:
    # top correlations by absolute value excluding self
    failure_assoc = corr["has_failure"].drop(labels=["has_failure"]).dropna().sort_values(key=np.abs, ascending=False)
    top_assoc = failure_assoc.head(5)
    insights.append("Top numeric factors linked to failure (by absolute correlation):")
    for feat, val in top_assoc.items():
        insights.append(f"  - {feat}: correlation={val:.3f}")

if "risk_level" in df.columns and "has_failure" in df.columns:
    risk_stats = df.groupby("risk_level")["has_failure"].mean().sort_values(ascending=False)
    insights.append("Failure rates by risk level suggest prioritization order:")
    for idx, val in risk_stats.items():
        insights.append(f"  - {idx}: failure_rate={val:.3%}")

if "has_maint" in df.columns and "has_failure" in df.columns:
    maint_stats = df.groupby("has_maint")["has_failure"].mean()
    if len(maint_stats) == 2:
        insights.append(
            "Maintenance relationship: compare failure rates for maintained vs non-maintained periods "
            "to optimize preventive maintenance timing."
        )

if "model" in df.columns and "has_failure" in df.columns:
    top_model = df.groupby("model")["has_failure"].mean().sort_values(ascending=False).head(1)
    if not top_model.empty:
        model_name = top_model.index[0]
        model_rate = float(top_model.iloc[0])
        insights.append(
            f"Model risk: model '{model_name}' shows highest observed failure rate ({model_rate:.3%}); "
            "consider targeted reliability interventions."
        )

# Generic business recommendations
insights.extend([
    "Operational recommendation: prioritize inspections for machines with low health_score and high vibration/pressure profiles.",
    "Planning recommendation: align maintenance schedules before observed monthly failure peaks.",
    "Modeling recommendation: use sensor + event flags + risk segmentation as baseline features for predictive models.",
])

for line in insights:
    print(line)


# ==============================
# Step 11 — Optional Interactive Output
# ==============================
if PLOTLY_AVAILABLE and "has_failure" in df.columns and "health_score" in df.columns:
    fig = px.scatter(
        df.sample(min(5000, len(df)), random_state=42),
        x="health_score",
        y="vibration" if "vibration" in df.columns else "health_score",
        color="has_failure",
        title="Interactive View: Health Score vs Vibration by Failure Outcome",
        opacity=0.7,
    )
    fig.show()

print("\nEDA completed. Charts and summaries are ready for executive reporting and predictive modeling support.")
