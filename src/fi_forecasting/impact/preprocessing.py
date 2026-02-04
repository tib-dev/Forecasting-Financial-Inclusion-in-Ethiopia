import pandas as pd
import numpy as np

def clean_fi_data(df):
    """
    Basic preprocessing for Ethiopia FI dataset.
    - Drops rows without observation_date
    - Fills missing pillar values with 'unknown'
    - Converts value_numeric to float
    - Fills key categorical columns with 'unknown'

    Raises:
        ValueError: if required columns are missing
    """
    required_cols = ['observation_date', 'pillar', 'record_type', 'indicator_code', 'category', 'source_name']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")

    # Drop rows missing observation_date
    df = df.dropna(subset=['observation_date'])

    # Fill missing pillar values
    df['pillar'] = df['pillar'].fillna('unknown')

    # Ensure numeric conversion
    if 'value_numeric' in df.columns:
        df['value_numeric'] = pd.to_numeric(df['value_numeric'], errors='coerce')

    # Fill missing categorical columns
    for col in ['record_type', 'indicator_code', 'category', 'source_name']:
        df[col] = df[col].fillna('unknown')

    return df


def add_growth_rate(df, indicator_code):
    """
    Add year-on-year growth rate for a specific indicator.
    - Creates a new column 'growth_rate' in df for the specified indicator.
    
    Raises:
        ValueError: if indicator_code not found in df
    """
    if indicator_code not in df['indicator_code'].values:
        raise ValueError(f"Indicator '{indicator_code}' not found in dataset")

    sub = df[df['indicator_code'] == indicator_code].sort_values('observation_date')
    sub['growth_rate'] = sub['value_numeric'].pct_change() * 100

    # Add back to main df
    df.loc[sub.index, 'growth_rate'] = sub['growth_rate']
    return df
