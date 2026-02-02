from __future__ import annotations

import re
from typing import Dict, List, Optional, Any, Callable
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Constants & helpers
# ---------------------------------------------------------------------

MIN_TEXT_LEN = 3


def _safe_get(row: pd.Series, idx: int) -> Optional[Any]:
    """Safely extract a value from a row by index."""
    try:
        val = row.iloc[idx]
        return val if pd.notna(val) else None
    except IndexError:
        return None


def _is_valid_text(value: Any, min_len: int = MIN_TEXT_LEN) -> bool:
    return isinstance(value, str) and len(value.strip()) > min_len


def _generate_code(prefix: str, name: str, max_len: int = 25) -> str:
    """
    Generate a normalized indicator code.
    Example: DIR_MOBILE_MONEY_USERS
    """
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name.upper()).strip("_")
    code = f"{prefix}_{cleaned}"
    return code[:max_len]


def _iterate_rows(
    df: pd.DataFrame,
    start_row: int,
    handler: Callable[[pd.Series], Optional[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Generic row iterator with row handler."""
    results: List[Dict[str, Any]] = []

    for idx, row in df.iterrows():
        if idx < start_row:
            continue

        try:
            item = handler(row)
            if item:
                results.append(item)
        except Exception as exc:
            logger.warning("Skipping row %s due to error: %s", idx, exc)

    return results


# ---------------------------------------------------------------------
# Sheet processors
# ---------------------------------------------------------------------

def extract_alternative_sources(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract alternative baseline sources (Sheet A)."""

    def handler(row: pd.Series) -> Optional[Dict[str, Any]]:
        name = _safe_get(row, 1)
        if not _is_valid_text(name):
            return None

        return {
            "source_name": name.strip(),
            "source_type": _safe_get(row, 2),
            "source_url": _safe_get(row, 6),
        }

    return _iterate_rows(df, start_row=7, handler=handler)


def extract_direct_indicators(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract direct correlation indicators (Sheet B)."""

    def handler(row: pd.Series) -> Optional[Dict[str, Any]]:
        name = _safe_get(row, 1)
        if not _is_valid_text(name):
            return None

        pillar = (
            "ACCESS"
            if any(k in name.lower() for k in ("account", "agent"))
            else "USAGE"
        )

        return {
            "indicator": name.strip(),
            "indicator_code": _generate_code("DIR", name),
            "correlation": _safe_get(row, 2),
            "why_matters": _safe_get(row, 3),
            "source": _safe_get(row, 4),
            "pillar": pillar,
        }

    return _iterate_rows(df, start_row=8, handler=handler)


def extract_indirect_indicators(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract indirect/proxy indicators (Sheet C)."""

    def handler(row: pd.Series) -> Optional[Dict[str, Any]]:
        name = _safe_get(row, 1)
        if not _is_valid_text(name):
            return None

        return {
            "indicator": name.strip(),
            "indicator_code": _generate_code("IND", name),
            "correlation": _safe_get(row, 2),
            "why_matters": _safe_get(row, 3),
            "source": _safe_get(row, 4),
            "pillar": "ACCESS",
        }

    return _iterate_rows(df, start_row=8, handler=handler)


def extract_market_nuances(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract market nuances (Sheet D)."""

    def handler(row: pd.Series) -> Optional[Dict[str, Any]]:
        theme = _safe_get(row, 1)
        if not _is_valid_text(theme):
            return None

        return {
            "theme": theme.strip(),
            "what_to_watch": _safe_get(row, 2),
            "market_impact": _safe_get(row, 3),
        }

    return _iterate_rows(df, start_row=6, handler=handler)


# ---------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------

def process_additional_data_points(
    sheets: Dict[str, pd.DataFrame]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Process all Additional Data Points sheets.

    Expected keys:
    - alternative_baselines
    - direct_correlation
    - indirect_correlation
    - market_nuances
    """

    if not sheets:
        logger.info("No additional data sheets provided.")
        return {
            "alternative_sources": [],
            "direct_indicators": [],
            "indirect_indicators": [],
            "market_notes": [],
        }

    return {
        "alternative_sources": extract_alternative_sources(
            sheets.get("alternative_baselines", pd.DataFrame())
        ),
        "direct_indicators": extract_direct_indicators(
            sheets.get("direct_correlation", pd.DataFrame())
        ),
        "indirect_indicators": extract_indirect_indicators(
            sheets.get("indirect_correlation", pd.DataFrame())
        ),
        "market_notes": extract_market_nuances(
            sheets.get("market_nuances", pd.DataFrame())
        ),
    }
