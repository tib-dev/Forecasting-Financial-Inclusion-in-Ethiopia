import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

logger = logging.getLogger(__name__)


class DataVisualizer:
    """Create visualizations for financial inclusion data."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set plotting style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")

    def plot_record_type_distribution(self, df: pd.DataFrame, filename: str = "record_type_distribution.png"):
        """Plot distribution of record types."""
        if df.empty or 'record_type' not in df.columns:
            logger.warning("Cannot plot record type distribution: missing data or column")
            return

        fig, ax = plt.subplots(figsize=(10, 6))

        record_counts = df['record_type'].value_counts()
        colors = plt.cm.Set3(range(len(record_counts)))

        record_counts.plot(kind='bar', ax=ax, color=colors, edgecolor='black')

        ax.set_title('Record Type Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Record Type', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.tick_params(axis='x', rotation=45)

        # Add value labels
        for i, v in enumerate(record_counts):
            ax.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved record type distribution plot: {filename}")

    def plot_temporal_coverage(self, observations: pd.DataFrame, filename: str = "temporal_coverage.png"):
        """Plot temporal coverage of observations."""
        if observations.empty or 'observation_date' not in observations.columns:
            logger.warning("Cannot plot temporal coverage: missing data or column")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Plot 1: Observations by year
        observations['year'] = pd.to_datetime(observations['observation_date']).dt.year
        yearly_counts = observations['year'].value_counts().sort_index()

        ax1.bar(yearly_counts.index, yearly_counts.values, color='steelblue', alpha=0.7)
        ax1.set_title('Number of Observations by Year', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Year', fontsize=12)
        ax1.set_ylabel('Count', fontsize=12)
        ax1.grid(True, alpha=0.3)

        # Plot 2: Indicator coverage heatmap
        if 'indicator_code' in observations.columns:
            # Create pivot table for heatmap
            pivot_data = observations.pivot_table(
                index='year',
                columns='indicator_code',
                values='value_numeric',
                aggfunc='count'
            ).fillna(0)

            # Select indicators with data in at least 2 years
            valid_indicators = pivot_data.columns[pivot_data.sum() > 0]
            if len(valid_indicators) > 0:
                # Take top 15 indicators for readability
                top_indicators = pivot_data[valid_indicators].sum().nlargest(15).index
                heatmap_data = pivot_data[top_indicators]

                im = ax2.imshow(heatmap_data.T, aspect='auto', cmap='YlOrRd')
                ax2.set_title('Indicator Coverage Heatmap (Top 15)', fontsize=14, fontweight='bold')
                ax2.set_xlabel('Year', fontsize=12)
                ax2.set_ylabel('Indicator', fontsize=12)
                ax2.set_xticks(range(len(heatmap_data.index)))
                ax2.set_xticklabels(heatmap_data.index, rotation=45)
                ax2.set_yticks(range(len(heatmap_data.columns)))
                ax2.set_yticklabels(heatmap_data.columns)

                # Add colorbar
                plt.colorbar(im, ax=ax2, label='Observation Count')
            else:
                ax2.text(0.5, 0.5, 'No valid indicators for heatmap',
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Indicator Coverage Heatmap', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved temporal coverage plot: {filename}")

    def plot_findex_trends(self, observations: pd.DataFrame, filename: str = "findex_trends.png"):
        """Plot Findex trends for Ethiopia."""
        # Define key Findex indicators
        findex_indicators = ['ACC_OWNERSHIP', 'USG_DIGITAL_PAYMENT', 'ACC_MM_ACCOUNT']

        # Filter for Findex data
        findex_mask = (
            (observations['source_name'].str.contains('Findex', case=False, na=False)) |
            (observations['indicator_code'].isin(findex_indicators))
        )

        findex_data = observations[findex_mask].copy()

        if findex_data.empty:
            logger.warning("No Findex data found for plotting")
            return

        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot each indicator with different styles
        styles = {
            'ACC_OWNERSHIP': {'color': '#2E86AB', 'marker': 'o', 'linewidth': 2.5},
            'USG_DIGITAL_PAYMENT': {'color': '#A23B72', 'marker': 's', 'linewidth': 2},
            'ACC_MM_ACCOUNT': {'color': '#F18F01', 'marker': '^', 'linewidth': 2}
        }

        for indicator in findex_indicators:
            ind_data = findex_data[findex_data['indicator_code'] == indicator]
            if not ind_data.empty:
                ind_data = ind_data.sort_values('observation_date')

                style = styles.get(indicator, {})
                ax.plot(
                    ind_data['observation_date'],
                    ind_data['value_numeric'],
                    label=f"{indicator.replace('_', ' ').title()}",
                    **style
                )

                # Add data point annotations
                for _, row in ind_data.iterrows():
                    ax.annotate(
                        f"{row['value_numeric']:.1f}%",
                        xy=(row['observation_date'], row['value_numeric']),
                        xytext=(0, 10),
                        textcoords='offset points',
                        ha='center',
                        fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7)
                    )

        ax.set_title('Financial Inclusion Trends in Ethiopia (Global Findex)',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=14)
        ax.set_ylabel('Percentage (%)', fontsize=14)
        ax.legend(fontsize=12, loc='upper left')
        ax.grid(True, alpha=0.3, linestyle='--')

        # Add a horizontal line at 50% for reference
        ax.axhline(y=50, color='gray', linestyle=':', alpha=0.5, label='50% Reference')

        # Improve x-axis formatting
        ax.xaxis.set_tick_params(rotation=45)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved Findex trends plot: {filename}")

    def plot_event_timeline(self, events: pd.DataFrame, filename: str = "event_timeline.png"):
        """Plot event timeline visualization."""
        if events.empty or 'event_date' not in events.columns:
            logger.warning("Cannot plot event timeline: missing data or column")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Plot 1: Event timeline
        events = events.copy()
        events['event_datetime'] = pd.to_datetime(events['event_date'])
        events['year'] = events['event_datetime'].dt.year

        # Create timeline plot
        years = sorted(events['year'].unique())
        y_positions = {}

        for i, year in enumerate(years):
            year_events = events[events['year'] == year]
            y_positions[year] = i

        # Plot each event
        if 'category' in events.columns and 'title' in events.columns:
            categories = events['category'].unique()
            category_colors = plt.cm.tab10(range(len(categories)))
            color_map = {cat: color for cat, color in zip(categories, category_colors)}

            for _, event in events.iterrows():
                year = event['year']
                category = event['category']
                title = event['title'][:30] + '...' if len(event['title']) > 30 else event['title']

                ax1.scatter(
                    event['event_datetime'],
                    y_positions[year],
                    color=color_map.get(category, 'gray'),
                    s=100,
                    alpha=0.7,
                    edgecolor='black'
                )

                # Add event label
                ax1.annotate(
                    title,
                    xy=(event['event_datetime'], y_positions[year]),
                    xytext=(10, 0),
                    textcoords='offset points',
                    fontsize=8,
                    verticalalignment='center'
                )

        ax1.set_yticks(list(y_positions.values()))
        ax1.set_yticklabels(list(y_positions.keys()))
        ax1.set_title('Event Timeline', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='x')

        # Plot 2: Event categories distribution
        if 'category' in events.columns:
            category_counts = events['category'].value_counts()
            colors = [color_map.get(cat, 'gray') for cat in category_counts.index]

            ax2.bar(category_counts.index, category_counts.values, color=colors)
            ax2.set_title('Event Distribution by Category', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Category', fontsize=12)
            ax2.set_ylabel('Count', fontsize=12)
            ax2.tick_params(axis='x', rotation=45)

            # Add value labels
            for i, v in enumerate(category_counts.values):
                ax2.text(i, v + 0.5, str(v), ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=150, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved event timeline plot: {filename}")
