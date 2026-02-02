import pandas as pd
from fi_forecasting.core.settings import get_settings

settings= get_settings()

def load_unified_excel():
    cfg = settings.get("datasets", {}).get("unified_excel", {})
    path = settings.root / cfg.get("path")

    if not path.exists():
        raise FileNotFoundError(f"Unified Excel not found: {path}")

    # Main sheet
    df_main = pd.read_excel(path, sheet_name=cfg.get("main_sheet"))

    # Impact sheet (optional)
    try:
        df_impact = pd.read_excel(path, sheet_name=cfg.get("impact_sheet"))
    except Exception:
        df_impact = pd.DataFrame()

    # Align schemas
    all_cols = sorted(set(df_main.columns).union(df_impact.columns))
    df_main = df_main.reindex(columns=all_cols)
    df_impact = df_impact.reindex(columns=all_cols)

    return pd.concat([df_main, df_impact], ignore_index=True)


def load_reference_codes_excel():
    cfg = settings.get("datasets", {}).get("reference_codes_excel", {})
    path = settings.root / cfg.get("path")

    if not path.exists():
        raise FileNotFoundError(f"Reference codes Excel not found: {path}")

    xls = pd.ExcelFile(path)
    if len(xls.sheet_names) == 1:
        return pd.read_excel(path, sheet_name=xls.sheet_names[0])

    return pd.concat(
        [pd.read_excel(path, sheet_name=s) for s in xls.sheet_names],
        ignore_index=True,
    )


def load_additional_data_guide():
    cfg = settings.get("datasets", {}).get("additional_data_guide", {})
    path = settings.root / cfg.get("path")

    if not path.exists():
        return None

    xls = pd.ExcelFile(path)
    return {
        "alternative_baselines": pd.read_excel(xls, sheet_name=0),
        "direct_correlation": pd.read_excel(xls, sheet_name=1),
        "indirect_correlation": pd.read_excel(xls, sheet_name=2),
        "market_nuances": pd.read_excel(xls, sheet_name=3),
    }
