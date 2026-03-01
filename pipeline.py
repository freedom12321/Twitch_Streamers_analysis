#!/usr/bin/env python3
"""Data pipeline for Twitch loyalty analysis."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

RAW_DATA_PATH = Path("data/raw/Twitch Live-Streaming Interactions Dataset.csv")
CLEAN_DATA_PATH = Path("data/cleaned.csv")
REPORT_PATH = Path("reports/data_cleaning_report.md")

COLUMN_NAMES = [
    "language_cluster_id",
    "session_id",
    "channel_login",
    "viewer_id",
    "engagement_rank",
]
VIEWER_MIN, VIEWER_MAX = 0, 6147
ENGAGEMENT_MIN, ENGAGEMENT_MAX = 1, 6148

def load_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load raw Twitch interaction data."""
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset at {path}")
    dtype_map = {
        "language_cluster_id": "int32",
        "session_id": "int64",
        "channel_login": "string",
        "viewer_id": "int16",
        "engagement_rank": "int16",
    }
    df = pd.read_csv(
        path,
        header=None,
        names=COLUMN_NAMES,
        dtype=dtype_map,
    )
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize Twitch interaction records."""
    cleaned = df.copy()
    cleaned["channel_login"] = (
        cleaned["channel_login"].astype("string").str.strip().str.lower()
    )
    cleaned = cleaned[cleaned["channel_login"] != ""]

    in_viewer_range = cleaned["viewer_id"].between(VIEWER_MIN, VIEWER_MAX)
    in_engagement_range = cleaned["engagement_rank"].between(
        ENGAGEMENT_MIN, ENGAGEMENT_MAX
    )
    cleaned = cleaned[in_viewer_range & in_engagement_range]

    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned

def validate_data(df: pd.DataFrame) -> Dict[str, int]:
    """Validate cleaned data and return summary of validation checks."""
    issues = {
        "missing_values": int(df.isna().sum().sum()),
        "empty_channel_names": int((df["channel_login"] == "").sum()),
        "viewer_out_of_range": int(
            (~df["viewer_id"].between(VIEWER_MIN, VIEWER_MAX)).sum()
        ),
        "engagement_out_of_range": int(
            (~df["engagement_rank"].between(ENGAGEMENT_MIN, ENGAGEMENT_MAX)).sum()
        ),
        "duplicate_rows": int(df.duplicated().sum()),
    }
    if any(issues.values()):
        raise ValueError(f"Validation failed: {issues}")
    return issues

def generate_report(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame, report_path: Path = REPORT_PATH) -> None:
    """Write a concise markdown cleaning report."""
    removed_rows = len(raw_df) - len(cleaned_df)
    missing_summary = raw_df.isna().sum().rename("missing_count")
    # Basic outlier detection: values outside expected id ranges
    outlier_mask = ~raw_df["viewer_id"].between(VIEWER_MIN, VIEWER_MAX)
    engagement_outliers = ~raw_df["engagement_rank"].between(ENGAGEMENT_MIN, ENGAGEMENT_MAX)
    report_lines = [
        "# Data Cleaning Report",
        "",
        "## Dataset Snapshot",
        f"- Raw rows: {len(raw_df):,}",
        f"- Clean rows: {len(cleaned_df):,}",
        f"- Rows removed: {removed_rows:,}",
        f"- Unique channels: {cleaned_df['channel_login'].nunique():,}",
        f"- Unique viewers (sampled IDs): {cleaned_df['viewer_id'].nunique():,}",
        "",
        "## Missingness",
    ]
    report_lines.extend(
        f"- {col}: {int(count):,}" for col, count in missing_summary.items()
    )
    report_lines.extend(
        [
            "",
            "## Outlier Checks",
            f"- Viewer IDs outside {VIEWER_MIN}-{VIEWER_MAX}: {int(outlier_mask.sum()):,}",
            f"- Engagement ranks outside {ENGAGEMENT_MIN}-{ENGAGEMENT_MAX}: {int(engagement_outliers.sum()):,}",
        ]
    )
    report_lines.extend(
        [
            "",
            "## Notes",
            "- Standardized channel logins to lowercase and trimmed whitespace.",
            "- Removed duplicate rows (if any) to avoid double-counting interactions.",
            "- Filtered implausible viewer/engagement ids outside the observed ID range.",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines))

def main() -> None:
    raw_df = load_data()
    cleaned_df = clean_data(raw_df)
    validate_data(cleaned_df)
    CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(CLEAN_DATA_PATH, index=False)
    generate_report(raw_df, cleaned_df)
    print(f"Saved cleaned data to {CLEAN_DATA_PATH}")
    print(f"Cleaning report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
