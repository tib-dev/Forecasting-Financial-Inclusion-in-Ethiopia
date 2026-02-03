from typing import Dict, List
import pandas as pd


REQUIRED_COLUMNS: List[str] = [
    "record_id",
    "record_type",
    "pillar",
    "indicator",
    "indicator_code",
    "value_numeric",
    "observation_date",
    "category",
    "parent_id",
    "source_name",
    "source_url",
    "confidence",
    "original_text",
    "collected_by",
    "collection_date",
    "notes",
]


VALID_RECORD_TYPES = {
    "observation",
    "event",
    "impact_link",
    "target",
}


def validate_required_columns(df: pd.DataFrame) -> None:
    """
    Validate presence of required columns in unified dataset.

    Raises
    ------
    ValueError
        If any required column is missing.
    """
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def validate_record_types(df: pd.DataFrame) -> None:
    """
    Ensure record_type contains only allowed values.
    """
    invalid = set(df["record_type"].dropna()) - VALID_RECORD_TYPES
    if invalid:
        raise ValueError(f"Invalid record_type values: {invalid}")


def validate_non_null_observations(df: pd.DataFrame) -> None:
    """
    Ensure numeric values exist for observation records.
    """
    obs = df[df["record_type"] == "observation"]
    if obs["value_numeric"].isna().any():
        raise ValueError("Observation records contain null value_numeric")
