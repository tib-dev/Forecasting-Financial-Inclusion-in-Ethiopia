from pathlib import Path
from datetime import datetime
from fi_forecasting.core.project_root import get_project_root

root=get_project_root()
log_path = root / "docs" / "data_enrichment_log.md"
def log_addition(
    record_id: str,
    record_type: str,
    indicator: str,
    source: str,
    confidence: str,
    notes: str,
    log_path: Path = log_path
):
    """
    Append a single record addition to a markdown log file.

    Parameters:
        record_id: Unique record identifier
        record_type: 'observation' or 'indicator_definition'
        indicator: Indicator name
        source: Data source
        confidence: Confidence level (low/medium/high)
        notes: Any additional notes
        log_path: Path to markdown log file
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"- [{now}] ({record_type}) {record_id}: {indicator} | "
        f"Source: {source} | Confidence: {confidence} | Notes: {notes}\n"
    )

    with log_path.open("a", encoding="utf-8") as f:
        f.write(log_entry)
