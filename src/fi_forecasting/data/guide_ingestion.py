from __future__ import annotations

import pandas as pd
from datetime import datetime
from typing import List, Dict, Callable


# -------------------------------------------------
# Core helpers
# -------------------------------------------------

def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def append_records(
    df: pd.DataFrame,
    records: List[Dict],
) -> pd.DataFrame:
    """
    Append a list of record dicts to a DataFrame safely.
    """
    if not records:
        return df

    return pd.concat(
        [df, pd.DataFrame.from_records(records)],
        ignore_index=True
    )


# -------------------------------------------------
# Indicator definitions ingestion
# -------------------------------------------------

def add_indicator_definitions(
    df_enriched: pd.DataFrame,
    indicator_defs: List[Dict],
    log_fn: Callable | None = None,
) -> pd.DataFrame:
    """
    Add new indicator definitions to the enriched dataset.
    """
    df_enriched = append_records(df_enriched, indicator_defs)

    if log_fn:
        for ind in indicator_defs:
            log_fn(
                record_id=ind.get("record_id"),
                record_type="indicator_definition",
                indicator=ind.get("indicator"),
                source="Additional Data Points Guide",
                confidence=ind.get("confidence"),
                notes=f"From {ind.get('category')} indicators",
            )

    return df_enriched


# -------------------------------------------------
# Observation ingestion from guide
# -------------------------------------------------

def add_guide_observations(
    df_enriched: pd.DataFrame,
    observations: List[Dict],
    collected_by: str = "Data Scientist",
    log_fn: Callable | None = None,
) -> pd.DataFrame:
    """
    Add placeholder or estimated observations derived from the guide.
    """

    enriched_obs = []

    for obs in observations:
        enriched = {
            **obs,
            "collection_date": obs.get("collection_date", _now()),
            "collected_by": obs.get("collected_by", collected_by),
        }
        enriched_obs.append(enriched)

    df_enriched = append_records(df_enriched, enriched_obs)

    if log_fn:
        for obs in enriched_obs:
            log_fn(
                record_id=obs["record_id"],
                record_type="observation",
                indicator=obs["indicator"],
                source=obs["source_name"],
                confidence=obs["confidence"],
                notes=obs.get("notes"),
            )

    return df_enriched
