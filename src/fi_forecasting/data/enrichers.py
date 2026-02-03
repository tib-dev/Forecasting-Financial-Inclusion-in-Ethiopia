from __future__ import annotations

import pandas as pd
from datetime import datetime
from typing import Dict, Callable, List

from fi_forecasting.data.additional_parsers import process_additional_data_points
from fi_forecasting.data.guide_ingestion import (
    add_indicator_definitions,
    add_guide_observations,
)


def _build_indicator_definitions(
    indicators: List[Dict],
    category: str,
    start_idx: int,
) -> List[Dict]:
    records = []
    idx = start_idx

    for ind in indicators:
        idx += 1
        records.append(
            {
                "record_id": f"IND_DEF_{idx:05d}",
                "record_type": "indicator_definition",
                "pillar": ind["pillar"],
                "indicator": ind["indicator"],
                "indicator_code": ind["indicator_code"],
                "indicator_direction": (
                    "positive"
                    if "positive" in str(ind.get("correlation", "")).lower()
                    else "negative"
                ),
                "source_name": ind.get("source", "Multiple"),
                "confidence": "medium",
                "category": category,
                "notes": ind.get("why_matters"),
                "collected_by": "Data Scientist",
                "collection_date": datetime.now().strftime("%Y-%m-%d"),
            }
        )

    return records


def enrich_dataset(
    df_unified: pd.DataFrame,
    additional_data: Dict,
    log_fn: Callable | None = None,
) -> pd.DataFrame:
    """
    Task-1 enrichment orchestrator.
    """

    parsed = process_additional_data_points(additional_data)

    direct = parsed.get("direct_indicators", [])
    indirect = parsed.get("indirect_indicators", [])

    # -------------------------
    # Indicator definitions
    # -------------------------
    existing_defs = df_unified.query(
        "record_type == 'indicator_definition'"
    )

    start_idx = (
        existing_defs["record_id"]
        .str.extract(r"(\d+)$")[0]
        .astype(float)
        .max()
    )
    start_idx = int(start_idx) if pd.notna(start_idx) else 1000

    indicator_defs = (
        _build_indicator_definitions(direct, "direct_correlation", start_idx)
        + _build_indicator_definitions(indirect, "indirect_correlation", start_idx + 100)
    )

    df_enriched = add_indicator_definitions(
        df_enriched=df_unified,
        indicator_defs=indicator_defs,
        log_fn=log_fn,
    )

    # -------------------------
    # Guide-derived observations (placeholders)
    # -------------------------
    guide_observations = []

    for ind in direct + indirect:
        guide_observations.append(
            {
                "record_id": f"OBS_GUIDE_{ind['indicator_code']}",
                "record_type": "observation",
                "pillar": ind["pillar"],
                "indicator": ind["indicator"],
                "indicator_code": ind["indicator_code"],
                "value_numeric": None,
                "observation_date": None,
                "source_name": ind.get("source"),
                "confidence": "medium",
                "notes": ind.get("why_matters"),
            }
        )

    df_enriched = add_guide_observations(
        df_enriched=df_enriched,
        observations=guide_observations,
        log_fn=log_fn,
    )

    return df_enriched
