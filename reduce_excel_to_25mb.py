import os
import math
import tempfile

import pandas as pd

# -----------------------------
# Configuration
# -----------------------------
INPUT_FILE = "/mnt/data/cleaned_predictive_maintenance.xlsx"
OUTPUT_FILE = "cleaned_predictive_maintenance_25MB.xlsx"
TARGET_SIZE_MB = 25.0
RANDOM_SEED = 42


def file_size_mb(path: str) -> float:
    """Return file size in megabytes (MB)."""
    return os.path.getsize(path) / (1024 * 1024)


def sample_rows(df: pd.DataFrame, n_rows: int, seed: int = 42) -> pd.DataFrame:
    """Randomly sample rows without changing columns."""
    n_rows = max(1, min(n_rows, len(df)))
    return df.sample(n=n_rows, random_state=seed).sort_index()


def estimate_initial_rows(total_rows: int, original_size_mb: float, target_size_mb: float) -> int:
    """Estimate row count to keep using direct size ratio."""
    if original_size_mb <= target_size_mb:
        return total_rows

    ratio = target_size_mb / original_size_mb
    estimated_rows = int(math.floor(total_rows * ratio))
    return max(1, min(estimated_rows, total_rows))


def write_and_measure(df: pd.DataFrame, path: str) -> float:
    """Write dataframe to Excel and return resulting file size in MB."""
    df.to_excel(path, index=False)
    return file_size_mb(path)


def find_best_row_count(df: pd.DataFrame, target_size_mb: float, seed: int = 42) -> int:
    """
    Find row count that gets file size close to target by:
    1) ratio-based initial estimate,
    2) binary search refinement.
    """
    total_rows = len(df)

    # Measure original file saved as-is (for robust estimation if source metadata differs)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_full:
        tmp_full_path = tmp_full.name
    try:
        current_size = write_and_measure(df, tmp_full_path)
    finally:
        if os.path.exists(tmp_full_path):
            os.remove(tmp_full_path)

    initial_rows = estimate_initial_rows(total_rows, current_size, target_size_mb)

    # If already small enough, keep all rows.
    if current_size <= target_size_mb:
        return total_rows

    # Binary search for largest row count that stays <= target size.
    low, high = 1, total_rows
    best = initial_rows

    # Ensure starting point is valid for "best" tracking.
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_init:
        tmp_init_path = tmp_init.name
    try:
        sampled_init = sample_rows(df, initial_rows, seed)
        init_size = write_and_measure(sampled_init, tmp_init_path)
        if init_size <= target_size_mb:
            best = initial_rows
        else:
            high = max(1, initial_rows - 1)
    finally:
        if os.path.exists(tmp_init_path):
            os.remove(tmp_init_path)

    # Refine with binary search.
    while low <= high:
        mid = (low + high) // 2

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_mid:
            tmp_mid_path = tmp_mid.name

        try:
            sampled_mid = sample_rows(df, mid, seed)
            mid_size = write_and_measure(sampled_mid, tmp_mid_path)
        finally:
            if os.path.exists(tmp_mid_path):
                os.remove(tmp_mid_path)

        if mid_size <= target_size_mb:
            best = mid
            low = mid + 1
        else:
            high = mid - 1

    return best


def main():
    # -----------------------------
    # 1) Read source Excel file
    # -----------------------------
    df = pd.read_excel(INPUT_FILE)

    original_size = file_size_mb(INPUT_FILE)
    original_rows = len(df)

    # -----------------------------
    # 2) Compute how many rows to keep
    # -----------------------------
    target_rows = find_best_row_count(df, TARGET_SIZE_MB, seed=RANDOM_SEED)

    # -----------------------------
    # 3) Randomly sample rows only
    #    (all columns preserved exactly)
    # -----------------------------
    reduced_df = sample_rows(df, target_rows, seed=RANDOM_SEED)

    # -----------------------------
    # 4) Save reduced dataset
    # -----------------------------
    reduced_df.to_excel(OUTPUT_FILE, index=False)

    # -----------------------------
    # 5) Print summary
    # -----------------------------
    new_size = file_size_mb(OUTPUT_FILE)
    new_rows = len(reduced_df)

    print(f"Original file size: {original_size:.2f} MB")
    print(f"New file size: {new_size:.2f} MB")
    print(f"Original row count: {original_rows}")
    print(f"New row count: {new_rows}")


if __name__ == "__main__":
    main()
