import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from fi_forecasting.data.additional_parsers import process_additional_data_points

REFERENCE_KEY = "record_id"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _generate_observation_record(
    indicator: Dict,
    observation_date: str | None,
) -> Dict:
    """
    Create a unified observation record following schema rules.
    """
    return {
        "record_type": "observation",
        "pillar": indicator.get("pillar"),
        "indicator": indicator.get("indicator"),
        "indicator_code": indicator.get("indicator_code"),
        "value_numeric": indicator.get("value_numeric"),
        "observation_date": observation_date,
        "source_name": indicator.get("source"),
        "source_url": indicator.get("source_url"),
        "confidence": indicator.get("confidence", "medium"),
        "original_text": indicator.get("original_text"),
        "collected_by": indicator.get("collected_by", "Analyst"),
        "collection_date": indicator.get(
            "collection_date", datetime.now().strftime("%Y-%m-%d")
        ),
        "notes": indicator.get("why_matters"),
    }


def _generate_indicator_definitions(
    indicators: List[Dict],
    category: str,
    start_idx: int,
) -> List[Dict]:
    """
    Create indicator_definition records for documentation & reuse.
    """
    records = []
    counter = start_idx

    for ind in indicators:
        counter += 1
        records.append(
            {
                "record_id": f"IND_DEF_{counter:05d}",
                "record_type": "indicator_definition",
                "pillar": ind.get("pillar"),
                "indicator": ind.get("indicator"),
                "indicator_code": ind.get("indicator_code"),
                "indicator_direction": (
                    "positive"
                    if "positive" in str(ind.get("correlation", "")).lower()
                    else "negative"
                ),
                "source_name": ind.get("source", "Multiple"),
                "source_url": ind.get("source_url"),
                "confidence": "medium",
                "collected_by": "Data Scientist",
                "collection_date": datetime.now().strftime("%Y-%m-%d"),
                "category": category,
                "notes": ind.get("why_matters"),
            }
        )

    return records


def _append_to_log(log_path: Path, section: str, records: List[Dict]) -> None:
    """
    Append enrichment actions to markdown log.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)

    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {section} — {datetime.now().strftime('%Y-%m-%d')}\n")
        for rec in records[:5]:
            f.write(f"- {rec}\n")
        if len(records) > 5:
            f.write(f"... +{len(records) - 5} more\n")


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def enrich_dataset(
    df_unified: pd.DataFrame,
    additional_data: Dict,
    log_path: Path,
    observation_date: str | None = None,
) -> pd.DataFrame:
    """
    Enrich unified dataset with additional indicators and documentation.

    Returns:
        Updated unified DataFrame.
    """
    parsed = process_additional_data_points(additional_data)

    direct = parsed.get("direct_indicators", [])
    indirect = parsed.get("indirect_indicators", [])

    # -------------------------
    # Observations
    # -------------------------
    observation_records = [
        _generate_observation_record(ind, observation_date)
        for ind in (direct + indirect)
    ]

    obs_df = pd.DataFrame(observation_records)
    obs_df = obs_df.reindex(columns=df_unified.columns)

    # -------------------------
    # Indicator definitions
    # -------------------------
    max_id = (
        df_unified[REFERENCE_KEY]
        .dropna()
        .astype(str)
        .str.extract(r"(\d+)$")[0]
        .astype(float)
        .max()
    )
    start_idx = int(max_id) if pd.notna(max_id) else 1000

    indicator_defs = (
        _generate_indicator_definitions(direct, "direct_correlation", start_idx)
        + _generate_indicator_definitions(indirect, "indirect_correlation", start_idx + 100)
    )

    ind_def_df = pd.DataFrame(indicator_defs)
    ind_def_df = ind_def_df.reindex(columns=df_unified.columns)

    # -------------------------
    # Merge
    # -------------------------
    enriched_df = pd.concat(
        [df_unified, obs_df, ind_def_df], ignore_index=True
    )

    # -------------------------
    # Logging
    # -------------------------
    if observation_records:
        _append_to_log(log_path, "New Observation Records", observation_records)

    if indicator_defs:
        _append_to_log(log_path, "New Indicator Definitions", indicator_defs)

    _append_to_log(
        log_path,
        "Alternative Sources",
        parsed.get("alternative_sources", []),
    )

    _append_to_log(
        log_path,
        "Market Nuances",
        parsed.get("market_notes", []),
    )

    return enriched_df
