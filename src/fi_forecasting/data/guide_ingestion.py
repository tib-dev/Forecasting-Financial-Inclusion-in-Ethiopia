from __future__ import annotations

import pandas as pd
from datetime import datetime
from typing import List, Dict, Callable


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
        ignore_index=True,
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
    Add indicator_definition records to the dataset.
    """
    df_enriched = append_records(df_enriched, indicator_defs)

    if log_fn:
        for ind in indicator_defs:
            log_fn(
                record_id=ind["record_id"],
                record_type="indicator_definition",
                description=ind["indicator"],
                source_url="Additional Data Points Guide",
                confidence=ind["confidence"],
                justification=ind.get("notes"),
            )

    return df_enriched


# -------------------------------------------------
# Guide-derived observations ingestion
# -------------------------------------------------

def add_guide_observations(
    df_enriched: pd.DataFrame,
    observations: List[Dict],
    collected_by: str = "Data Scientist",
    log_fn: Callable | None = None,
) -> pd.DataFrame:
    """
    Add observations derived from the Additional Data Points Guide.
    """

    enriched_obs = []

    for obs in observations:
        enriched_obs.append(
            {
                **obs,
                "collected_by": obs.get("collected_by", collected_by),
                "collection_date": obs.get("collection_date", _now()),
            }
        )

    df_enriched = append_records(df_enriched, enriched_obs)

    if log_fn:
        for obs in enriched_obs:
            log_fn(
                record_id=obs["record_id"],
                record_type="observation",
                description=obs["indicator"],
                source_url=obs.get("source_url"),
                confidence=obs["confidence"],
                justification=obs.get("notes"),
            )

    return df_enriched


