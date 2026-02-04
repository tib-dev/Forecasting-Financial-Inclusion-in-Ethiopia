# ==================================================
# impact_model.py - Updated for merged_df column names
# ==================================================

import pandas as pd

# -----------------------------
# 1. Merge events with impact links
# -----------------------------
def merge_events_impact(events_df: pd.DataFrame, impact_links_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge events with their impact links using 'record_id' from events
    and 'parent_id' from impact links. Fills missing indicator codes
    from related_indicator if needed.
    """
    df_links = impact_links_df.copy()

    # Ensure we have a column named 'indicator_code'
    if 'indicator_code' not in df_links.columns or df_links['indicator_code'].isna().all():
        if 'related_indicator' in df_links.columns:
            df_links['indicator_code'] = df_links['related_indicator']
        else:
            df_links['indicator_code'] = 'UNKNOWN'

    merged_df = events_df.merge(
        df_links,
        how='left',  # keep all events
        left_on='record_id',
        right_on='parent_id',
        suffixes=('_event', '_link')
    )

    # Fill missing indicator_code column
    if 'indicator_code' not in merged_df.columns:
        merged_df['indicator_code'] = merged_df.get('related_indicator_link', 'UNKNOWN')
    else:
        merged_df['indicator_code'] = merged_df['indicator_code'].fillna(
            merged_df.get('related_indicator_link', 'UNKNOWN')
        )

    return merged_df


# -----------------------------
# 2. Compute effect values
# -----------------------------
def apply_event_effects(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # columns
    event_col = "record_id_event"
    ind_col = "indicator_code"

    # ---- MAP MAGNITUDE (THIS IS THE REAL ISSUE) ----
    magnitude_map = {
        "low": 5,
        "medium": 15,
        "high": 25
    }

    df["impact_magnitude"] = (
        df["impact_magnitude_link"]
        .str.lower()
        .map(magnitude_map)
        .fillna(0)
    )

    df["lag_months"] = pd.to_numeric(
        df["lag_months_link"], errors="coerce"
    ).fillna(0)

    # ---- EFFECT MODEL ----
    df["effect_value"] = df["impact_magnitude"]

    return df[
        [event_col, ind_col, "impact_magnitude", "lag_months", "effect_value"]
    ]




# -----------------------------
# 3. Build Event-Indicator Association Matrix
# -----------------------------
def build_event_indicator_matrix(
    df: pd.DataFrame,
    event_col='record_id_event',
    indicator_col='indicator_code',
    effect_col='effect_value'
) -> pd.DataFrame:
    """
    Pivot table of events vs indicators with effect values.
    """
    if df.empty:
        return pd.DataFrame()  # return empty if no data

    pivot = df.pivot_table(
        index=event_col,
        columns=indicator_col,
        values=effect_col,
        aggfunc='sum',
        fill_value=0
    )
    return pivot
