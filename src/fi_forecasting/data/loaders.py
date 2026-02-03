from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from fi_forecasting.core.settings import settings


def load_unified_excel() -> pd.DataFrame:
    """
    Load the unified Ethiopia financial inclusion Excel dataset.

    The Excel file is expected to contain:
    - A main sheet with observations, events, and targets
    - An optional impact_links sheet

    Both sheets are aligned to a unified schema and concatenated.

    Returns
    -------
    pd.DataFrame
        Unified dataset containing all record types.

    Raises
    ------
    FileNotFoundError
        If the configured Excel file does not exist.
    ValueError
        If the main sheet is missing or empty.
    """
    cfg = settings.get("datasets", {}).get("unified_excel", {})
    path = settings.root / cfg.get("path", "")
    main_sheet = cfg.get("main_sheet")
    impact_sheet = cfg.get("impact_sheet")

    if not path.exists():
        raise FileNotFoundError(f"Unified Excel not found: {path}")

    if not main_sheet:
        raise ValueError("Main sheet name not configured for unified_excel")

    xls = pd.ExcelFile(path)

    if main_sheet not in xls.sheet_names:
        raise ValueError(
            f"Main sheet '{main_sheet}' not found in {path.name}"
        )

    df_main = pd.read_excel(xls, sheet_name=main_sheet)

    if df_main.empty:
        raise ValueError("Main unified sheet is empty")

    # Impact sheet is optional
    if impact_sheet and impact_sheet in xls.sheet_names:
        df_impact = pd.read_excel(xls, sheet_name=impact_sheet)
    else:
        df_impact = pd.DataFrame(columns=df_main.columns)

    # Align schemas deterministically
    all_columns = sorted(set(df_main.columns).union(df_impact.columns))
    df_main = df_main.reindex(columns=all_columns)
    df_impact = df_impact.reindex(columns=all_columns)

    return pd.concat([df_main, df_impact], ignore_index=True)


def load_reference_codes_excel() -> pd.DataFrame:
    """
    Load reference codes from an Excel file.

    Supports:
    - Single-sheet Excel
    - Multi-sheet Excel (concatenated)

    Returns
    -------
    pd.DataFrame
        Reference codes table.
    """
    cfg = settings.get("datasets", {}).get("reference_codes_excel", {})
    path = settings.root / cfg.get("path", "")

    if not path.exists():
        raise FileNotFoundError(f"Reference codes Excel not found: {path}")

    xls = pd.ExcelFile(path)

    frames = [
        pd.read_excel(xls, sheet_name=sheet)
        for sheet in xls.sheet_names
    ]

    df = pd.concat(frames, ignore_index=True)

    if df.empty:
        raise ValueError("Reference codes Excel contains no data")

    return df


def load_additional_data_guide() -> Optional[Dict[str, pd.DataFrame]]:
    """
    Load the Additional Data Points Guide Excel.

    Expected sheets:
    0 - Alternative Baselines
    1 - Direct Correlation
    2 - Indirect Correlation
    3 - Market Nuances

    Returns
    -------
    dict[str, pd.DataFrame] or None
        Dictionary of guide sheets, or None if file not found.
    """
    cfg = settings.get("datasets", {}).get("additional_data_guide", {})
    path = settings.root / cfg.get("path", "")

    if not path.exists():
        return None

    xls = pd.ExcelFile(path)

    return {
        "alternative_baselines": pd.read_excel(xls, sheet_name=0),
        "direct_correlation": pd.read_excel(xls, sheet_name=1),
        "indirect_correlation": pd.read_excel(xls, sheet_name=2),
        "market_nuances": pd.read_excel(xls, sheet_name=3),
    }
