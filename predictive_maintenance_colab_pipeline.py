"""
Predictive Maintenance Data Engineering Pipeline (Google Colab)

This script:
1) Loads 5 predictive maintenance datasets
2) Cleans each dataset
3) Merges them into a BI-ready master dataset
4) Creates analytical features
5) Exports a final CSV for BI and ML workflows
"""

import numpy as np
import pandas as pd


# ------------------------------
# Step 1 & 2: Load datasets
# ------------------------------
telemetry_path = "/content/PdM_telemetry.csv.zip"
errors_path = "/content/PdM_errors.csv"
maint_path = "/content/PdM_maint.csv"
failures_path = "/content/PdM_failures.csv"
machines_path = "/content/PdM_machines.csv"

telemetry = pd.read_csv(telemetry_path, compression="zip")
errors = pd.read_csv(errors_path)
maint = pd.read_csv(maint_path)
failures = pd.read_csv(failures_path)
machines = pd.read_csv(machines_path)


# ------------------------------
# Step 3: Data cleaning helpers
# ------------------------------
def clean_time_series(df: pd.DataFrame, has_datetime: bool = True) -> pd.DataFrame:
    """Clean dataset by parsing datetime, removing duplicates, sorting, and resetting index."""
    cleaned = df.copy()

    if has_datetime and "datetime" in cleaned.columns:
        cleaned["datetime"] = pd.to_datetime(cleaned["datetime"], errors="coerce")
        # Keep rows even if other fields are valid; only remove rows with invalid datetime in time-series tables
        cleaned = cleaned.dropna(subset=["datetime"])

    cleaned = cleaned.drop_duplicates()

    sort_cols = ["machineID"]
    if has_datetime and "datetime" in cleaned.columns:
        sort_cols.append("datetime")

    cleaned = cleaned.sort_values(sort_cols).reset_index(drop=True)
    return cleaned


def clean_master_table(df: pd.DataFrame) -> pd.DataFrame:
    """Clean non-time-series master table."""
    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates().sort_values(["machineID"]).reset_index(drop=True)
    return cleaned


telemetry = clean_time_series(telemetry, has_datetime=True)
errors = clean_time_series(errors, has_datetime=True)
maint = clean_time_series(maint, has_datetime=True)
failures = clean_time_series(failures, has_datetime=True)
machines = clean_master_table(machines)


# ------------------------------
# Step 4: Merge datasets
# ------------------------------
# 1) telemetry + machines on machineID
master_df = telemetry.merge(machines, how="left", on="machineID")

# 2) merge errors on machineID + datetime
master_df = master_df.merge(errors, how="left", on=["machineID", "datetime"])

# 3) merge maintenance on machineID + datetime
master_df = master_df.merge(maint, how="left", on=["machineID", "datetime"])

# 4) merge failures on machineID + datetime
master_df = master_df.merge(failures, how="left", on=["machineID", "datetime"])


# ------------------------------
# Step 5: Missing value handling
# ------------------------------
numeric_cols = master_df.select_dtypes(include=[np.number]).columns
categorical_cols = master_df.select_dtypes(include=["object", "category"]).columns

# Fill numeric columns with mean (if a column is all NaN, mean stays NaN; we keep it)
for col in numeric_cols:
    master_df[col] = master_df[col].fillna(master_df[col].mean())

# Fill categorical columns with "None" for BI-friendly explicit missingness
master_df[categorical_cols] = master_df[categorical_cols].fillna("None")


# ------------------------------
# Step 6: Feature engineering
# ------------------------------
# Time-based features
master_df["year"] = master_df["datetime"].dt.year
master_df["month"] = master_df["datetime"].dt.month
master_df["day"] = master_df["datetime"].dt.day
master_df["hour"] = master_df["datetime"].dt.hour
master_df["dayofweek"] = master_df["datetime"].dt.dayofweek

# Event flags
master_df["has_error"] = np.where(master_df["errorID"] != "None", 1, 0)
master_df["has_maint"] = np.where(master_df["comp"] != "None", 1, 0)
master_df["has_failure"] = np.where(master_df["failure"] != "None", 1, 0)

# Machine age category
def age_to_category(age):
    if age < 5:
        return "Young"
    if 5 <= age <= 10:
        return "Mid"
    return "Old"


master_df["age_category"] = master_df["age"].apply(age_to_category)


# ------------------------------
# Step 7: Health score
# ------------------------------
master_df["health_score"] = (
    100
    - (master_df["vibration"] * 2)
    - (master_df["pressure"] * 0.05)
    - (master_df["has_error"] * 10)
)
master_df["health_score"] = master_df["health_score"].clip(lower=0)


# ------------------------------
# Step 8: Final dataset checks
# ------------------------------
print("Final dataset shape:", master_df.shape)
print("\nFinal dataset info:")
print(master_df.info())
print("\nFirst 5 rows:")
print(master_df.head())


# ------------------------------
# Step 9: Export final dataset
# ------------------------------
output_path = "cleaned_predictive_maintenance.csv"
master_df.to_csv(output_path, index=False)
print(f"\nSaved final dataset to: {output_path}")

# Google Colab download helper
from google.colab import files  # noqa: E402

files.download(output_path)
