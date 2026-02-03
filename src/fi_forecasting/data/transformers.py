import pandas as pd
from pathlib import Path


def load_reference_codes(path: Path) -> pd.DataFrame:
    """
    Load reference codes CSV.

    Expected columns:
    - field
    - valid_value
    """
    df = pd.read_csv(path)
    if not {"field", "valid_value"}.issubset(df.columns):
        raise ValueError("Invalid reference_codes schema")
    return df


def validate_against_reference_codes(
    df: pd.DataFrame,
    reference_df: pd.DataFrame,
) -> None:
    """
    Validate categorical fields using reference_codes table.
    """
    for field in reference_df["field"].unique():
        valid = set(
            reference_df.loc[
                reference_df["field"] == field, "valid_value"
            ]
        )
        observed = set(df[field].dropna())
        invalid = observed - valid
        if invalid:
            raise ValueError(
                f"Invalid values for {field}: {sorted(invalid)}"
            )
