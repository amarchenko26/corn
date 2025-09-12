#!/usr/bin/env python3
"""
Agricultural Census Government Payments Analysis

This script analyzes government payments data from the agricultural census
across different years, focusing on the United States level data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_merged_data():
    """Load the merged census data."""
    data_path = Path("/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/interim/census_merged_1992_2012.tsv")
    
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        logger.error("Please run collect_census_data.py first to create the merged dataset.")
        return None
    
    try:
        df = pd.read_csv(data_path, sep='\t', low_memory=False)
        logger.info(f"Loaded merged data: {len(df)} rows, {len(df.columns)} columns")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None

def filter_us_data(df):
    """Filter data for United States level (level==3 or name==UNITED STATES)."""
    logger.info("Filtering for United States data...")
    
    # Check what values are in the level and name columns
    logger.info(f"Unique values in 'level' column: {df['level'].unique()}")
    logger.info(f"Unique values in 'name' column: {df['name'].unique()}")
    
    # Filter for US data using both criteria
    us_data = df[
        (df['level'] == 3) | 
        (df['name'].str.contains('UNITED STATES', case=False, na=False))
    ].copy()
    
    logger.info(f"Found {len(us_data)} US-level records")
    
    if len(us_data) == 0:
        logger.warning("No US-level data found. Checking all records...")
        logger.info("Sample of data:")
        print(df[['year', 'name', 'level', 'gov_payments_avg']].head(10))
        return None
    
    return us_data

def pivot_to_wide_format(df):
    """Pivot the data from long to wide format."""
    logger.info("Pivoting data to wide format...")
    
    # Create a pivot table with years as columns
    pivot_df = df.pivot_table(
        index=['name', 'level', 'fips', 'statefip', 'counfip'],
        columns='year',
        values='gov_payments_avg',
        aggfunc='mean'  # In case there are duplicates
    ).reset_index()
    
    # Flatten column names
    pivot_df.columns.name = None
    
    logger.info(f"Pivoted data shape: {pivot_df.shape}")
    logger.info(f"Columns: {list(pivot_df.columns)}")
    
    return pivot_df

def create_time_series_plot(df, pivot_df):
    """Create a time series plot of government payments over time."""
    logger.info("Creating time series plot...")
    
    # Set up the plot style
    plt.style.use('seaborn-v0_8')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Time series of government payments
    years = sorted([col for col in pivot_df.columns if isinstance(col, (int, float)) and 1990 <= col <= 2020])
    gov_payments = [pivot_df[year].iloc[0] if year in pivot_df.columns else np.nan for year in years]
    
    ax1.plot(years, gov_payments, marker='o', linewidth=2, markersize=8, color='#2E86AB')
    ax1.set_title('Average Government Payments per Farm in the United States\nAgricultural Census 1992-2012', 
                  fontsize=14, fontweight='bold')
    ax1.set_xlabel('Census Year', fontsize=12)
    ax1.set_ylabel('Average Government Payments per Farm ($)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(years)
    
    # Add value labels on points
    for i, (year, value) in enumerate(zip(years, gov_payments)):
        if not pd.isna(value):
            ax1.annotate(f'${value:,.0f}', 
                        (year, value), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontsize=10)
    
    # Plot 2: Bar chart for better comparison
    ax2.bar(years, gov_payments, color='#A23B72', alpha=0.7, edgecolor='black', linewidth=0.5)
    ax2.set_title('Government Payments per Farm by Census Year', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Census Year', fontsize=12)
    ax2.set_ylabel('Average Government Payments per Farm ($)', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_xticks(years)
    
    # Add value labels on bars
    for i, (year, value) in enumerate(zip(years, gov_payments)):
        if not pd.isna(value):
            ax2.text(year, value + max(gov_payments) * 0.01, f'${value:,.0f}', 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the plot
    output_dir = Path("/Users/anyamarchenko/Documents/GitHub/corn/output/figs")
    plot_path = output_dir / "government_payments_timeseries.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    logger.info(f"Plot saved to: {plot_path}")
    
    plt.show()
    
    return years, gov_payments



def main():
    """Main function to run the analysis."""
    logger.info("Starting government payments analysis...")
    
    # Load the merged data
    df = load_merged_data()
    if df is None:
        return
    
    # Filter for US data
    us_data = filter_us_data(df)
    if us_data is None:
        logger.error("Could not find US-level data. Exiting.")
        return
    
    # Pivot to wide format
    pivot_df = pivot_to_wide_format(us_data)
    
    # Create visualizations
    years, gov_payments = create_time_series_plot(us_data, pivot_df)
        
    # Additional analysis
    logger.info("\nAdditional Analysis:")
    logger.info(f"Years with data: {[year for year, value in zip(years, gov_payments) if not pd.isna(value)]}")
    logger.info(f"Years missing data: {[year for year, value in zip(years, gov_payments) if pd.isna(value)]}")
    
    if len([v for v in gov_payments if not pd.isna(v)]) > 1:
        # Calculate percentage change
        valid_values = [(year, value) for year, value in zip(years, gov_payments) if not pd.isna(value)]
        if len(valid_values) >= 2:
            first_year, first_value = valid_values[0]
            last_year, last_value = valid_values[-1]
            pct_change = ((last_value - first_value) / first_value) * 100
            logger.info(f"Change from {first_year} to {last_year}: {pct_change:.1f}%")
    
    logger.info("Analysis completed successfully!")

if __name__ == "__main__":
    main()
