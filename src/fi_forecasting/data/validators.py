import pandas as pd

REQUIRED_COLUMNS = {
    "record_id",
    "record_type",
    "pillar",
    "indicator",
    "indicator_code",
    "value_numeric",
    "observation_date",
    "source_name",
    "confidence",
}

def validate_unified_schema(df):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")


# Validate against reference codes

def _get_valid_codes(ref_codes: pd.DataFrame, field_name: str) -> set[str]:
    """Support both reference_codes.csv (field/valid_values) and reference_codes.xlsx (field/code)."""
    if ref_codes is None or ref_codes.empty:
        return set()

    if 'field' not in ref_codes.columns:
        return set()

    ref_subset = ref_codes[ref_codes['field'].astype(str) == str(field_name)]

    if 'valid_values' in ref_subset.columns:
        # CSV-style: comma-separated list in one row
        series = ref_subset['valid_values'].dropna().astype(str)
        if series.empty:
            return set()
        return {v.strip() for v in series.iloc[0].split(',') if v.strip()}

    if 'code' in ref_subset.columns:
        # XLSX-style: one code per row
        return {str(v).strip() for v in ref_subset['code'].dropna().astype(str).tolist() if str(v).strip()}

    return set()


def validate_field(df: pd.DataFrame, field_name: str, ref_codes: pd.DataFrame) -> None:
    valid_values = _get_valid_codes(ref_codes, field_name)
    if not valid_values:
        print(f"No reference codes found for {field_name}")
        return

    if field_name not in df.columns:
        print(f"Field {field_name} not present in dataset")
        return

    actual_values = {str(v).strip() for v in df[field_name].dropna().astype(str).tolist() if str(v).strip()}
    invalid = sorted([v for v in actual_values if v not in valid_values])

    if invalid:
        print(f"Invalid values in {field_name}: {invalid}")
    else:
        print(f"{field_name}: All values valid")


