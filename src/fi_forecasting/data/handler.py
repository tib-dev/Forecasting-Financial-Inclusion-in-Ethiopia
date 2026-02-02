import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Union, Literal, Optional, Any
import logging
import joblib

from fi_forecasting.core.settings import settings

logger = logging.getLogger(__name__)


class DataHandler:
    """
    DataHandler manages all I/O operations for the project.

    Supported:
    - Tabular data (csv, parquet, excel, json)
    - Serialized objects (pkl, joblib) via joblib
    - Plot saving

    Paths are resolved via the central settings registry.
    """

    def __init__(
        self,
        filepath: Union[str, Path],
        file_type: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the handler.

        Args:
            filepath: Full path to file
            file_type: Optional override of file type
            **kwargs: Passed to pandas/joblib I/O
        """
        self.filepath = Path(filepath)
        self.file_type = file_type.lower() if file_type else self.filepath.suffix.replace(".", "")
        self.kwargs = kwargs

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self) -> Any:
        """
        Load data or object from disk.

        Returns:
            DataFrame or Python object (for pkl/joblib)
        """
        try:
            if self.file_type == "csv":
                return pd.read_csv(self.filepath, **self.kwargs)

            if self.file_type == "parquet":
                return pd.read_parquet(self.filepath, **self.kwargs)

            if self.file_type in {"excel", "xlsx"}:
                return pd.read_excel(self.filepath, **self.kwargs)

            if self.file_type == "json":
                return pd.read_json(self.filepath, **self.kwargs)

            if self.file_type in {"pkl", "joblib"}:
                return joblib.load(self.filepath)

            raise ValueError(f"Unsupported load type: {self.file_type}")

        except Exception as e:
            logger.error(f"Failed to load file at {self.filepath}: {e}")
            raise

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self, obj: Any):
        """
        Save a DataFrame or Python object to disk.

        Args:
            obj: DataFrame (csv/parquet/…) or model/object (pkl/joblib)
        """
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            if self.file_type == "csv":
                obj.to_csv(self.filepath, index=self.kwargs.get(
                    "index", False), **self.kwargs)

            elif self.file_type == "parquet":
                obj.to_parquet(self.filepath, **self.kwargs)

            elif self.file_type in {"excel", "xlsx"}:
                obj.to_excel(self.filepath, index=self.kwargs.get(
                    "index", False), **self.kwargs)

            elif self.file_type == "json":
                obj.to_json(self.filepath, **self.kwargs)

            elif self.file_type in {"pkl", "joblib"}:
                joblib.dump(obj, self.filepath)

            else:
                raise ValueError(f"Unsupported save type: {self.file_type}")

            logger.info(f"File successfully saved to {self.filepath}")

        except Exception as e:
            logger.error(f"Failed to save file at {self.filepath}: {e}")
            raise

    # ------------------------------------------------------------------
    # Registry Factory
    # ------------------------------------------------------------------
    CoreSection = Literal["DATA", "REPORTS", "MODELS"]

    @classmethod
    def from_registry(
        cls,
        section: Union[CoreSection, str],
        path_key: str,
        filename: str,
        **kwargs
    ):
        """
        Create a DataHandler using paths defined in settings.

        Example:
            DataHandler.from_registry(
                section="MODELS",
                path_key="models_dir",
                filename="best_model.pkl"
            )
        """
        try:
            registry_section = getattr(settings.paths, section.upper())
            base_path = registry_section[path_key]
            full_path = base_path / filename
            return cls(filepath=full_path, **kwargs)

        except (AttributeError, KeyError) as e:
            logger.error(
                f"Path not found in registry: {section} -> {path_key}. Error: {e}"
            )
            raise

    # ------------------------------------------------------------------
    # Plot Saving
    # ------------------------------------------------------------------

    @staticmethod
    def save_plot(
        filename: str,
        fig: Optional[plt.Figure] = None,
        **kwargs
    ):
        """
        Save a matplotlib figure to the reports/plots directory.

        Args:
            filename: Output filename
            fig: Optional matplotlib Figure
        """
        plot_dir = settings.paths.REPORTS["plots_dir"]
        plot_dir.mkdir(parents=True, exist_ok=True)

        save_path = plot_dir / filename

        try:
            if fig:
                fig.savefig(save_path, bbox_inches="tight", **kwargs)
            else:
                plt.savefig(save_path, bbox_inches="tight", **kwargs)

            logger.info(f"Plot saved to: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"Failed to save plot {filename}: {e}")
            raise
