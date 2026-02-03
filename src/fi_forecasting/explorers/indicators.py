import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class IndicatorAnalyzer:
    """Analyze indicator patterns and distributions."""

    def __init__(self):
        self.sparse_threshold = 3  # Minimum observations for an indicator

    def analyze_distribution(self, observations: pd.DataFrame) -> Dict[str, Any]:
        """Analyze indicator frequency and distribution."""
        if observations.empty:
            return {}

        results = {
            'indicator_frequency': {},
            'indicator_stats': {},
            'data_gaps': [],
            'summary': {}
        }

        if 'indicator_code' in observations.columns:
            # Frequency analysis
            indicator_counts = observations['indicator_code'].value_counts()
            results['indicator_frequency'] = indicator_counts.head(20).to_dict()

            # Statistical summary for each indicator
            if 'value_numeric' in observations.columns:
                stats = observations.groupby('indicator_code')['value_numeric'].agg([
                    'count', 'mean', 'std', 'min', 'max', 'median'
                ]).round(2)
                results['indicator_stats'] = stats.to_dict('index')

            # Identify sparse indicators
            sparse_indicators = self._identify_sparse_indicators(indicator_counts)
            if sparse_indicators:
                results['data_gaps'].extend(sparse_indicators)

            # Summary statistics
            results['summary'] = {
                'total_indicators': len(indicator_counts),
                'indicators_with_data': len(observations['indicator_code'].unique()),
                'most_frequent': indicator_counts.index[0] if not indicator_counts.empty else None,
                'least_frequent': indicator_counts.index[-1] if not indicator_counts.empty else None
            }

        return results

    def _identify_sparse_indicators(self, indicator_counts: pd.Series) -> List[Dict[str, Any]]:
        """Identify indicators with insufficient data."""
        sparse_indicators = []

        for indicator, count in indicator_counts.items():
            if count < self.sparse_threshold:
                sparse_indicators.append({
                    'type': 'sparse_indicator',
                    'indicator': indicator,
                    'observation_count': count,
                    'severity': 'high' if count == 1 else 'medium'
                })

        return sparse_indicators

    def analyze_correlation(self, observations: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between indicators."""
        if observations.empty or 'indicator_code' not in observations.columns:
            return {}

        results = {
            'correlation_matrix': {},
            'strong_correlations': [],
            'weak_correlations': []
        }

        # Create pivot table for correlation analysis
        pivot_data = observations.pivot_table(
            index='observation_date',
            columns='indicator_code',
            values='value_numeric'
        )

        if not pivot_data.empty and len(pivot_data.columns) > 1:
            # Calculate correlation matrix
            corr_matrix = pivot_data.corr()
            results['correlation_matrix'] = corr_matrix.round(3).to_dict()

            # Identify strong correlations (|r| > 0.7)
            strong_pairs = []
            weak_pairs = []

            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    indicator1 = corr_matrix.columns[i]
                    indicator2 = corr_matrix.columns[j]
                    correlation = corr_matrix.iloc[i, j]

                    if abs(correlation) > 0.7:
                        strong_pairs.append({
                            'indicator1': indicator1,
                            'indicator2': indicator2,
                            'correlation': correlation
                        })
                    elif abs(correlation) < 0.3:
                        weak_pairs.append({
                            'indicator1': indicator1,
                            'indicator2': indicator2,
                            'correlation': correlation
                        })

            results['strong_correlations'] = strong_pairs
            results['weak_correlations'] = weak_pairs

        return results
