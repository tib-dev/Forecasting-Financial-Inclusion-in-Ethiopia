#!/usr/bin/env bash

# ==============================================================================
# init_setup.sh
# Project: Forecasting Financial Inclusion in Ethiopia
# Purpose: Bootstrap production-grade project structure
# Safe to re-run (idempotent)
# ==============================================================================

set -e
set -o pipefail

echo "======================================================"
echo "Initializing: Forecasting Financial Inclusion in Ethiopia"
echo "======================================================"

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
create_dir () {
  [ -d "$1" ] || mkdir -p "$1"
}

create_file () {
  [ -f "$1" ] || touch "$1"
}

# ------------------------------------------------------------------
# Root-level directories
# ------------------------------------------------------------------
dirs=(
  "config"
  "data/raw/finindex"
  "data/raw/operators"
  "data/raw/infrastructure"
  "data/staged"
  "data/curated"
  "data/reference"

  "notebooks"

  "src/fi_forecasting"
  "src/fi_forecasting/core"
  "src/fi_forecasting/data"
  "src/fi_forecasting/features"
  "src/fi_forecasting/events"
  "src/fi_forecasting/impact"
  "src/fi_forecasting/models"
  "src/fi_forecasting/forecasting"
  "src/fi_forecasting/evaluation"
  "src/fi_forecasting/pipeline"
  "src/fi_forecasting/utils"

  "dashboard/pages"
  "dashboard/assets"

  "reports/figures"

  "scripts"
  "tests"

  "docker"
  ".github/workflows"
)

for d in "${dirs[@]}"; do
  create_dir "$d"
done

echo "✓ Directory structure created"

# ------------------------------------------------------------------
# Python package files
# ------------------------------------------------------------------
py_files=(
  # Package root
  "src/fi_forecasting/__init__.py"

  # Core
  "src/fi_forecasting/core/__init__.py"
  "src/fi_forecasting/core/project_root.py"
  "src/fi_forecasting/core/settings.py"

  # Data
  "src/fi_forecasting/data/__init__.py"
  "src/fi_forecasting/data/loaders.py"
  "src/fi_forecasting/data/validators.py"
  "src/fi_forecasting/data/transformers.py"

  # Features
  "src/fi_forecasting/features/__init__.py"
  "src/fi_forecasting/features/engineering.py"
  "src/fi_forecasting/features/lag_features.py"

  # Events
  "src/fi_forecasting/events/__init__.py"
  "src/fi_forecasting/events/encoder.py"
  "src/fi_forecasting/events/calendars.py"

  # Impact modeling
  "src/fi_forecasting/impact/__init__.py"
  "src/fi_forecasting/impact/impact_links.py"
  "src/fi_forecasting/impact/impact_matrix.py"
  "src/fi_forecasting/impact/lag_models.py"

  # Models
  "src/fi_forecasting/models/__init__.py"
  "src/fi_forecasting/models/baseline.py"
  "src/fi_forecasting/models/regression.py"
  "src/fi_forecasting/models/diagnostics.py"

  # Forecasting
  "src/fi_forecasting/forecasting/__init__.py"
  "src/fi_forecasting/forecasting/scenarios.py"
  "src/fi_forecasting/forecasting/forecaster.py"
  "src/fi_forecasting/forecasting/uncertainty.py"

  # Evaluation
  "src/fi_forecasting/evaluation/__init__.py"
  "src/fi_forecasting/evaluation/metrics.py"
  "src/fi_forecasting/evaluation/backtesting.py"

  # Pipeline
  "src/fi_forecasting/pipeline/__init__.py"
  "src/fi_forecasting/pipeline/build_dataset.py"
  "src/fi_forecasting/pipeline/run_models.py"
  "src/fi_forecasting/pipeline/run_forecast.py"

  # Utils
  "src/fi_forecasting/utils/__init__.py"
  "src/fi_forecasting/utils/logger.py"
  "src/fi_forecasting/utils/paths.py"
  "src/fi_forecasting/utils/helpers.py"

  # Dashboard
  "dashboard/app.py"
  "dashboard/pages/overview.py"
  "dashboard/pages/trends.py"
  "dashboard/pages/events.py"
  "dashboard/pages/forecasts.py"

  # Tests
  "tests/__init__.py"
  "tests/test_data_validation.py"
  "tests/test_event_encoding.py"
  "tests/test_impact_links.py"
  "tests/test_forecasting.py"
)

for f in "${py_files[@]}"; do
  create_file "$f"
done

echo "✓ Python package files created"

# ------------------------------------------------------------------
# Configuration files
# ------------------------------------------------------------------
config_files=(
  "config/data.yaml"
  "config/indicators.yaml"
  "config/events.yaml"
  "config/model.yaml"
  "config/forecast.yaml"
  "config/logging.yaml"
)

for c in "${config_files[@]}"; do
  create_file "$c"
done

echo "✓ Configuration files created"

# ------------------------------------------------------------------
# Core project files
# ------------------------------------------------------------------
core_files=(
  "README.md"
  "data_enrichment_log.md"
  "pyproject.toml"
  "requirements.txt"
  ".gitignore"
  ".dockerignore"
)

for f in "${core_files[@]}"; do
  create_file "$f"
done

echo "✓ Core project files created"

# ------------------------------------------------------------------
# Scripts
# ------------------------------------------------------------------
scripts=(
  "scripts/run_pipeline.sh"
  "scripts/run_forecast.sh"
  "scripts/run_dashboard.sh"
)

for s in "${scripts[@]}"; do
  create_file "$s"
  chmod +x "$s"
done

echo "✓ Scripts created and executable"

# ------------------------------------------------------------------
# Final message
# ------------------------------------------------------------------
echo "======================================================"
echo "Project structure is ready."
echo "You now have a production-grade financial inclusion"
echo "forecasting platform scaffold."
echo "======================================================"
