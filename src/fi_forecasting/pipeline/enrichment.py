import pandas as pd
from pathlib import Path
from datetime import datetime
from fi_forecasting.data.enrichers import process_additional_data_points

# -----------------------------
# Helper functions
# -----------------------------

def generate_observation_record(indicator_dict, observation_date=None):
    """
    Create a unified observation record from extracted indicator info.
    """
    record = {
        'record_type': 'observation',
        'pillar': indicator_dict.get('pillar'),
        'indicator': indicator_dict.get('indicator'),
        'indicator_code': indicator_dict.get('indicator_code'),
        'value_numeric': None,  # Fill if actual value available
        'observation_date': observation_date,
        'source_name': indicator_dict.get('source'),
        'source_url': indicator_dict.get('source_url', None),
        'confidence': 'medium',  # Default
        'notes': indicator_dict.get('why_matters', '')
    }
    return record


def append_to_log(log_path: Path, records: list, section: str):
    """
    Append enrichment records to markdown log
    """
    now = datetime.now().strftime("%Y-%m-%d")
    log_path.touch(exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {section} ({now})\n")
        for rec in records[:5]:  # show first 5 for brevity
            f.write(f"- {rec}\n")
        if len(records) > 5:
            f.write(f"... +{len(records)-5} more\n")


# -----------------------------
# Main enrichment pipeline
# -----------------------------
def enrich_unified_dataset(df_unified: pd.DataFrame, additional_data: dict, log_path: Path, observation_date=None):

    enriched = process_additional_data_points(additional_data)

    new_obs_records = []

    direct = enriched.get('direct_indicators', [])
    indirect = enriched.get('indirect_indicators', [])

    for ind in direct + indirect:
        new_obs_records.append(
            generate_observation_record(ind, observation_date)
        )

    if new_obs_records:
        new_df = pd.DataFrame(new_obs_records)
        new_df = new_df.reindex(columns=df_unified.columns)
        df_unified = pd.concat([df_unified, new_df], ignore_index=True)
        append_to_log(log_path, new_obs_records, section="New Observation Records")

    append_to_log(
        log_path,
        enriched.get('alternative_sources', []),
        section="Alternative Sources"
    )

    append_to_log(
        log_path,
        enriched.get('market_notes', []),
        section="Market Nuances"
    )

    return df_unified
