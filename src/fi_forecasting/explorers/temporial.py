import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TemporalAnalyzer:
    """Analyze temporal patterns in financial inclusion data."""

    def analyze_coverage(self, observations: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal coverage of observations."""
        if observations.empty:
            return {}

        results = {
            'yearly_coverage': {},
            'monthly_coverage': {},
            'quarterly_coverage': {},
            'data_gaps': []
        }

        if 'observation_date' in observations.columns:
            # Convert to datetime and extract time components
            observations = observations.copy()
            observations['obs_datetime'] = pd.to_datetime(observations['observation_date'])
            observations['year'] = observations['obs_datetime'].dt.year
            observations['month'] = observations['obs_datetime'].dt.month
            observations['quarter'] = observations['obs_datetime'].dt.quarter

            # Yearly coverage
            yearly_counts = observations['year'].value_counts().sort_index()
            results['yearly_coverage'] = yearly_counts.to_dict()

            # Monthly coverage (for most recent year)
            if not yearly_counts.empty:
                recent_year = yearly_counts.index.max()
                recent_data = observations[observations['year'] == recent_year]
                monthly_counts = recent_data['month'].value_counts().sort_index()
                results['monthly_coverage'] = monthly_counts.to_dict()

            # Identify temporal gaps
            results['data_gaps'].extend(self._identify_temporal_gaps(yearly_counts))

        return results

    def _identify_temporal_gaps(self, yearly_counts: pd.Series) -> List[Dict[str, Any]]:
        """Identify gaps in yearly coverage."""
        gaps = []

        if len(yearly_counts) > 1:
            years = sorted(yearly_counts.index)
            expected_years = list(range(min(years), max(years) + 1))
            missing_years = [year for year in expected_years if year not in years]

            if missing_years:
                gaps.append({
                    'type': 'temporal_gap',
                    'missing_years': missing_years,
                    'gap_size': len(missing_years),
                    'severity': 'high' if len(missing_years) > 3 else 'medium'
                })

        return gaps

    def analyze_seasonality(self, observations: pd.DataFrame) -> Dict[str, Any]:
        """Analyze seasonal patterns in the data."""
        if observations.empty or 'observation_date' not in observations.columns:
            return {}

        results = {}

        # Extract month and quarter
        observations = observations.copy()
        observations['month'] = pd.to_datetime(observations['observation_date']).dt.month
        observations['quarter'] = pd.to_datetime(observations['observation_date']).dt.quarter

        # Analyze by indicator if available
        if 'indicator_code' in observations.columns:
            monthly_patterns = {}
            quarterly_patterns = {}

            for indicator in observations['indicator_code'].unique():
                ind_data = observations[observations['indicator_code'] == indicator]

                if not ind_data.empty and 'value_numeric' in ind_data.columns:
                    # Monthly pattern
                    monthly_avg = ind_data.groupby('month')['value_numeric'].mean()
                    monthly_patterns[indicator] = monthly_avg.to_dict()

                    # Quarterly pattern
                    quarterly_avg = ind_data.groupby('quarter')['value_numeric'].mean()
                    quarterly_patterns[indicator] = quarterly_avg.to_dict()

            results['monthly_patterns'] = monthly_patterns
            results['quarterly_patterns'] = quarterly_patterns

        return results
