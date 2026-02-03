from pathlib import Path
from datetime import datetime
from typing import Optional
from fi_forecasting.core.project_root import get_project_root

root = get_project_root()
DEFAULT_LOG_PATH = root / "docs" / "data_enrichment_log.md"


def log_addition(
    record_id: str,
    record_type: str,
    indicator: Optional[str] = None,
    source: Optional[str] = None,
    confidence: Optional[str] = None,
    notes: Optional[str] = None,
    *,
    description: Optional[str] = None,
    justification: Optional[str] = None,
    source_url: Optional[str] = None,
    log_path: Path = DEFAULT_LOG_PATH,
):
    """
    Append a single record addition to a markdown log file.

    Backward-compatible logger that supports both positional and
    keyword-based enrichment pipelines.
    """

    # -------------------------
    # Normalize aliases
    # -------------------------
    indicator = indicator or description or "N/A"
    source = source or source_url or "Unknown"
    notes = notes or justification or ""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = (
        f"- [{now}] ({record_type}) {record_id}: {indicator} | "
        f"Source: {source} | Confidence: {confidence or 'unknown'} | "
        f"Notes: {notes}\n"
    )

    with log_path.open("a", encoding="utf-8") as f:
        f.write(log_entry)
