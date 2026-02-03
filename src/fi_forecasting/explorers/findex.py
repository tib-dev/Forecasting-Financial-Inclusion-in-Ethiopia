import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class FindexAnalyzer:
    """Specialized analyzer for Global Findex data."""

    def __init__(self):
        self.findex_indicators = {
            'access': ['ACC_OWNERSHIP', 'ACC_BANK_ACCOUNT', 'ACC_MM_ACCOUNT'],
            'usage': ['USG_DIGITAL_PAYMENT', 'USG_MM_TRANSACTION', 'USG_ACCOUNT_RECEIVE_WAGES'],
            'other': ['ACC_FINANCIAL_INSTITUTION', 'USG_CARD_PAYMENT']
        }

    def analyze_trends(self, observations: pd.DataFrame) -> Dict[str, Any]:
        """Analyze Global Findex trends."""
        if observations.empty:
            return {}

        # Filter for Findex data
        findex_mask = (
            (observations['source_name'].str.contains('Findex', case=False, na=False)) |
            (observations['indicator_code'].isin([
                'ACC_OWNERSHIP', 'USG_DIGITAL_PAYMENT', 'ACC_MM_ACCOUNT'
            ]))
        )

        findex_data = observations[findex_mask].copy()

        if findex_data.empty:
            return {}

        results = {
            'account_ownership': self._analyze_indicator_trend(findex_data, 'ACC_OWNERSHIP'),
            'digital_payments': self._analyze_indicator_trend(findex_data, 'USG_DIGITAL_PAYMENT'),
            'mobile_money': self._analyze_indicator_trend(findex_data, 'ACC_MM_ACCOUNT'),
            'growth_analysis': {},
            'comparative_analysis': {}
        }

        # Calculate growth rates
        results['growth_analysis'] = self._calculate_growth_rates(findex_data)

        # Comparative analysis
        results['comparative_analysis'] = self._compare_indicators(findex_data)

        return results

    def _analyze_indicator_trend(self, data: pd.DataFrame, indicator: str) -> Dict[str, Any]:
        """Analyze trend for a specific indicator."""
        ind_data = data[data['indicator_code'] == indicator].copy()

        if ind_data.empty:
            return {}

        # Sort by date
        ind_data = ind_data.sort_values('observation_date')

        # Calculate statistics
        values = ind_data['value_numeric'].tolist()
        dates = ind_data['observation_date'].tolist()

        if len(values) >= 2:
            changes = [values[i] - values[i-1] for i in range(1, len(values))]
            growth_rates = [(values[i] - values[i-1]) / values[i-1] * 100
                          for i in range(1, len(values))]
        else:
            changes = []
            growth_rates = []

        return {
            'years': [d.year for d in dates],
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'values': values,
            'changes': changes,
            'growth_rates': growth_rates,
            'mean': np.mean(values) if values else None,
            'std': np.std(values) if len(values) > 1 else None,
            'trend': 'increasing' if len(values) > 1 and values[-1] > values[0] else
                    'decreasing' if len(values) > 1 and values[-1] < values[0] else
                    'stable'
        }

    def _calculate_growth_rates(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate growth rates between survey periods."""
        results = {}

        # Get unique years sorted
        years = sorted(pd.to_datetime(data['observation_date']).dt.year.unique())

        if len(years) >= 2:
            for indicator in ['ACC_OWNERSHIP', 'USG_DIGITAL_PAYMENT']:
                ind_data = data[data['indicator_code'] == indicator].copy()
                if not ind_data.empty:
                    ind_data = ind_data.sort_values('observation_date')

                    for i in range(1, len(ind_data)):
                        year1 = ind_data.iloc[i-1]['observation_date'].year
                        year2 = ind_data.iloc[i]['observation_date'].year
                        value1 = ind_data.iloc[i-1]['value_numeric']
                        value2 = ind_data.iloc[i]['value_numeric']

                        period = f"{year1}-{year2}"
                        if period not in results:
                            results[period] = {}

                        results[period][indicator] = {
                            'absolute_change': value2 - value1,
                            'percentage_change': ((value2 - value1) / value1 * 100) if value1 != 0 else None,
                            'compound_growth_rate': self._calculate_cagr(value1, value2, year2 - year1)
                        }

        return results

    def _calculate_cagr(self, start: float, end: float, years: int) -> float:
        """Calculate Compound Annual Growth Rate."""
        if start == 0 or years == 0:
            return 0
        return ((end / start) ** (1 / years) - 1) * 100

    def _compare_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Compare different Findex indicators."""
        results = {}

        # Group by year and compare indicators
        data['year'] = pd.to_datetime(data['observation_date']).dt.year

        for year in data['year'].unique():
            year_data = data[data['year'] == year]
            year_results = {}

            for indicator in ['ACC_OWNERSHIP', 'USG_DIGITAL_PAYMENT', 'ACC_MM_ACCOUNT']:
                ind_value = year_data[year_data['indicator_code'] == indicator]['value_numeric']
                if not ind_value.empty:
                    year_results[indicator] = float(ind_value.iloc[0])

            if year_results:
                results[str(year)] = year_results

        return results
