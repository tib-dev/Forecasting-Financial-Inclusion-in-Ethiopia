# src/fi_forecasting/data/handlers.py

from __future__ import annotations

from pathlib import Path
from typing import Optional, Any
import logging

import pandas as pd
import matplotlib.pyplot as plt
import joblib

from fi_forecasting.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ============================================================================
# Base
# ============================================================================

class BaseHandler:
    """
    Base class for all I/O handlers.

    Responsibilities:
    - Own a concrete filesystem path
    - Ensure parent directories exist
    - Provide consistent logging surface
    """

    def __init__(self, path: Path):
        self.path = path.resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.path.exists()


# ============================================================================
# Tabular Data (pandas)
# ============================================================================

class TabularHandler(BaseHandler):
    """
    Handler for tabular datasets (CSV, Parquet, Excel, JSON).

    Explicit methods only.
    No file-type inference.
    """

    # -------------------------
    # CSV
    # -------------------------
    def load_csv(self, **kwargs) -> pd.DataFrame:
        logger.info("Loading CSV: %s", self.path)
        return pd.read_csv(self.path, **kwargs)

    def save_csv(
        self,
        df: pd.DataFrame,
        *,
        index: bool = False,
        **kwargs,
    ) -> None:
        logger.info("Saving CSV: %s", self.path)
        df.to_csv(self.path, index=index, **kwargs)

    # -------------------------
    # Parquet
    # -------------------------
    def load_parquet(self, **kwargs) -> pd.DataFrame:
        logger.info("Loading Parquet: %s", self.path)
        return pd.read_parquet(self.path, **kwargs)

    def save_parquet(self, df: pd.DataFrame, **kwargs) -> None:
        logger.info("Saving Parquet: %s", self.path)
        df.to_parquet(self.path, **kwargs)

    # -------------------------
    # Excel
    # -------------------------
    def load_excel(
        self,
        sheet_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Returns:
            DataFrame or dict[str, DataFrame] if sheet_name=None
        """
        logger.info(
            "Loading Excel: %s (sheet=%s)", self.path, sheet_name
        )
        return pd.read_excel(
            self.path,
            sheet_name=sheet_name,
            **kwargs,
        )

    def save_excel(
        self,
        df: pd.DataFrame,
        *,
        index: bool = False,
        **kwargs,
    ) -> None:
        logger.info("Saving Excel: %s", self.path)
        df.to_excel(self.path, index=index, **kwargs)

    # -------------------------
    # JSON
    # -------------------------
    def load_json(self, **kwargs) -> pd.DataFrame:
        logger.info("Loading JSON: %s", self.path)
        return pd.read_json(self.path, **kwargs)

    def save_json(self, df: pd.DataFrame, **kwargs) -> None:
        logger.info("Saving JSON: %s", self.path)
        df.to_json(self.path, **kwargs)


# ============================================================================
# Serialized Objects (models, artifacts)
# ============================================================================

class ObjectHandler(BaseHandler):
    """
    Handler for serialized Python objects (joblib).
    """

    def load(self) -> Any:
        logger.info("Loading object: %s", self.path)
        return joblib.load(self.path)

    def save(self, obj: Any) -> None:
        logger.info("Saving object: %s", self.path)
        joblib.dump(obj, self.path)


# ============================================================================
# Plots
# ============================================================================

class PlotHandler(BaseHandler):
    """
    Handler for saving matplotlib figures.
    """

    def save(
        self,
        fig: Optional[plt.Figure] = None,
        **kwargs,
    ) -> Path:
        logger.info("Saving plot: %s", self.path)

        if fig is not None:
            fig.savefig(self.path, bbox_inches="tight", **kwargs)
        else:
            plt.savefig(self.path, bbox_inches="tight", **kwargs)

        return self.path


# ============================================================================
# Registry-backed Factory (the main entry point)
# ============================================================================

class HandlerFactory:
    """
    Factory that resolves paths via Settings.PathRegistry
    and returns strongly-typed handlers.

    This is the ONLY place that should touch settings.paths.
    """

    def __init__(self, settings_obj: Settings = settings):
        self.settings = settings_obj

    # -------------------------
    # Tabular
    # -------------------------
    def tabular(
        self,
        section: str,
        key: str,
        filename: str,
    ) -> TabularHandler:
        base = getattr(self.settings.paths, section.upper())[key]
        return TabularHandler(base / filename)

    # -------------------------
    # Objects / models
    # -------------------------
    def object(
        self,
        section: str,
        key: str,
        filename: str,
    ) -> ObjectHandler:
        base = getattr(self.settings.paths, section.upper())[key]
        return ObjectHandler(base / filename)

    # -------------------------
    # Plots
    # -------------------------
    def plot(self, filename: str) -> PlotHandler:
        base = self.settings.paths.REPORTS["figures"]
        return PlotHandler(base / filename)
