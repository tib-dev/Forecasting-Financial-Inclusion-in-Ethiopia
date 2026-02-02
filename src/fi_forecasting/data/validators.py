REQUIRED_COLUMNS = {
    "id",
    "record_type",
    "pillar",
    "indicator",
    "indicator_code",
    "value_numeric",
    "observation_date",
    "category",
    "source_name",
    "confidence"
}

def validate_unified_schema(df):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if not df["record_type"].isin(
        ["observation", "event", "impact_link", "target"]
    ).all():
        raise ValueError("Invalid record_type detected")

    return True
