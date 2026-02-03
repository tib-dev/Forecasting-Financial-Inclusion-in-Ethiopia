import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EventAnalyzer:
    """Analyze events and their impacts."""

    def __init__(self):
        self.event_categories = [
            'policy', 'product_launch', 'infrastructure',
            'market_entry', 'partnership', 'regulatory'
        ]

    def analyze_timeline(self, events: pd.DataFrame) -> Dict[str, Any]:
        """Analyze event timeline and categorization."""
        if events.empty:
            return {}

        results = {
            'timeline': {},
            'category_distribution': {},
            'annual_events': {},
            'event_density': 0,
            'impact_analysis': {}
        }

        if 'event_date' in events.columns:
            events = events.copy()
            events['year'] = pd.to_datetime(events['event_date']).dt.year
            events['month'] = pd.to_datetime(events['event_date']).dt.month
            events['quarter'] = pd.to_datetime(events['event_date']).dt.quarter

            # Annual events
            annual_counts = events['year'].value_counts().sort_index()
            results['annual_events'] = annual_counts.to_dict()

            # Event density
            if len(annual_counts) > 0:
                results['event_density'] = {
                    'events_per_year': len(events) / len(annual_counts),
                    'years_with_events': len(annual_counts),
                    'total_events': len(events)
                }

            # Monthly distribution for recent year
            if not annual_counts.empty:
                recent_year = annual_counts.index.max()
                recent_events = events[events['year'] == recent_year]
                monthly_counts = recent_events['month'].value_counts().sort_index()
                results['monthly_distribution'] = monthly_counts.to_dict()

        if 'category' in events.columns:
            category_counts = events['category'].value_counts()
            results['category_distribution'] = category_counts.to_dict()

            # Analyze category trends over time
            category_trends = {}
            if 'year' in events.columns:
                for category in self.event_categories:
                    cat_data = events[events['category'] == category]
                    if not cat_data.empty:
                        cat_years = cat_data['year'].value_counts().sort_index()
                        category_trends[category] = cat_years.to_dict()

            results['category_trends'] = category_trends

        return results

    def analyze_impacts(self, events: pd.DataFrame, impact_links: pd.DataFrame) -> Dict[str, Any]:
        """Analyze event impacts based on impact links."""
        if events.empty or impact_links.empty:
            return {}

        results = {
            'events_with_impacts': {},
            'impact_distribution': {},
            'lag_analysis': {},
            'magnitude_analysis': {}
        }

        # Merge events with impact links
        merged = pd.merge(
            events,
            impact_links,
            left_on='record_id',
            right_on='parent_id',
            how='left',
            suffixes=('_event', '_impact')
        )

        # Events with impacts
        events_with_impacts = merged[~merged['parent_id'].isna()]
        results['events_with_impacts'] = {
            'count': len(events_with_impacts['record_id'].unique()),
            'percentage': (len(events_with_impacts['record_id'].unique()) / len(events) * 100)
                         if len(events) > 0 else 0
        }

        # Impact distribution by category
        if 'category' in events_with_impacts.columns:
            category_impacts = events_with_impacts.groupby('category').agg({
                'record_id': 'nunique',
                'impact_magnitude': 'mean',
                'lag_months': 'mean'
            }).round(2)
            results['impact_distribution'] = category_impacts.to_dict('index')

        # Lag analysis
        if 'lag_months' in events_with_impacts.columns:
            lag_stats = events_with_impacts['lag_months'].agg([
                'count', 'mean', 'std', 'min', 'max', 'median'
            ]).round(1)
            results['lag_analysis'] = lag_stats.to_dict()

        # Magnitude analysis
        if 'impact_magnitude' in events_with_impacts.columns:
            magnitude_stats = events_with_impacts['impact_magnitude'].agg([
                'count', 'mean', 'std', 'min', 'max', 'median'
            ]).round(3)
            results['magnitude_analysis'] = magnitude_stats.to_dict()

            # Distribution by direction
            if 'impact_direction' in events_with_impacts.columns:
                direction_dist = events_with_impacts['impact_direction'].value_counts()
                results['direction_distribution'] = direction_dist.to_dict()

        return results
