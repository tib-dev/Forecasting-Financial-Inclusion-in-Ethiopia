from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional, Mapping
import logging
import os
import yaml

from fi_forecasting.core.project_root import get_project_root

logger = logging.getLogger(__name__)


# =====================================================
# YAML utilities
# =====================================================

def _load_yaml(path: Path) -> Dict[str, Any]:
    """
    Safely load a YAML file.
    Returns an empty dict if the file is missing or invalid.
    """
    if not path.exists():
        logger.debug("Config file not found: %s", path)
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ValueError("Top-level YAML structure must be a mapping")
        return data
    except Exception as exc:
        logger.warning("Failed to load YAML config %s: %s", path, exc)
        return {}


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge dictionaries.
    Values from override always take precedence.
    """
    merged: Dict[str, Any] = dict(base)

    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value

    return merged


def load_config(config_dir: Path) -> Dict[str, Any]:
    """
    Load and merge all YAML files in the config directory.

    Files are loaded in alphabetical order to ensure determinism.
    """
    if not config_dir.exists():
        logger.warning("Config directory does not exist: %s", config_dir)
        return {}

    merged: Dict[str, Any] = {}

    for path in sorted(config_dir.glob("*.yaml")):
        merged = _deep_merge(merged, _load_yaml(path))

    return merged


# =====================================================
# Path registry
# =====================================================

class PathRegistry:
    """
    Central registry for all filesystem paths defined in config.

    Supports:
      paths:
        data: "data/raw"
        reports:
          figures: "reports/figures"
    """

    def __init__(
        self,
        root: Path,
        config: Mapping[str, Any],
        create_dirs: bool = True,
    ):
        self.root = root.resolve()
        self._sections: Dict[str, Dict[str, Path]] = {}
        self._leaf_paths: Dict[str, Path] = {}

        paths_cfg = config.get("paths", {})
        if not isinstance(paths_cfg, dict):
            raise TypeError("Config key 'paths' must be a dictionary")

        self._process_paths(paths_cfg, create_dirs)

    # -------------------------------------------------

    def _process_paths(self, cfg: Dict[str, Any], create_dirs: bool) -> None:
        for key, value in cfg.items():
            key_lower = key.lower()

            if isinstance(value, dict):
                resolved: Dict[str, Path] = {}

                for subkey, subvalue in value.items():
                    path = self._resolve_path(subvalue)
                    if create_dirs:
                        path.mkdir(parents=True, exist_ok=True)

                    resolved[subkey] = path
                    self._leaf_paths[f"{key_lower}.{subkey}"] = path

                self._sections[key_lower] = resolved
                setattr(self, key.upper(), resolved)

            elif isinstance(value, (str, Path)):
                path = self._resolve_path(value)
                if create_dirs:
                    path.mkdir(parents=True, exist_ok=True)

                resolved = {"root": path}
                self._sections[key_lower] = resolved
                self._leaf_paths[key_lower] = path
                setattr(self, key.upper(), resolved)

            else:
                logger.warning(
                    "Invalid path specification for '%s': %s",
                    key,
                    type(value),
                )

    # -------------------------------------------------

    def _resolve_path(self, spec: Any) -> Path:
        if isinstance(spec, Path):
            return (self.root / spec).resolve()

        if isinstance(spec, str):
            return (self.root / spec).resolve()

        if isinstance(spec, dict) and "path" in spec:
            return (self.root / spec["path"]).resolve()

        raise TypeError(f"Invalid path specification: {spec}")

    # -------------------------------------------------

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a path or section.
        Supports dot notation for leaf paths.
        """
        key = key.lower()

        if key in self._sections:
            return self._sections[key]

        if key in self._leaf_paths:
            return self._leaf_paths[key]

        return default

    def __getitem__(self, key: str) -> Dict[str, Path]:
        return self._sections[key.lower()]

    def __getattr__(self, name: str) -> Dict[str, Path]:
        key = name.lower()
        if key in self._sections:
            return self._sections[key]
        raise AttributeError(f"'PathRegistry' has no attribute '{name}'")

    def as_dict(self) -> Dict[str, Dict[str, Path]]:
        return dict(self._sections)


# =====================================================
# Central settings object
# =====================================================

class Settings:
    """
    Central runtime configuration object.

    Example:
        settings = get_settings()
        settings.get("model.horizon")
        settings.paths.DATA["raw"]
    """

    def __init__(
        self,
        root: Optional[Path] = None,
        create_dirs: bool = True,
    ):
        self.root: Path = (root or get_project_root()).resolve()
        self.config: Dict[str, Any] = load_config(self.root / "config")
        self.paths = PathRegistry(self.root, self.config, create_dirs)

    # -------------------------------------------------

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve configuration values using dot notation.
        """
        current: Any = self.config

        for part in key.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current


# =====================================================
# Lazy singleton (import-safe)
# =====================================================

_SETTINGS: Optional[Settings] = None


def get_settings(create_dirs: bool = True) -> Settings:
    """
    Lazily initialize settings.
    Safe for imports, tests, and notebooks.
    """
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = Settings(create_dirs=create_dirs)
    return _SETTINGS
