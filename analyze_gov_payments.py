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


# Configuration variables
DATA_FILE_PATH          = "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/interim/census_merged_1992_2022_deflated.tsv"
OUTPUT_DIR              = "/Users/anyamarchenko/Documents/GitHub/corn/output"
FIGS_DIR                = "figs"
TABS_DIR                = "tabs"
PLOT_FILENAME           = "government_payments_timeseries.png"
GOV_PAYMENTS_COLUMN     = "gov_payments_avg_real"  # Use the deflated column
FARM_BILL_YEARS         = [1996, 2002, 2008, 2014, 2018, 2025]
FARM_BILL_LABELS        = ['1996 Farm Bill', '2002 Farm Bill', '2008 Farm Bill', '2014 Farm Bill', '2018 Farm Bill', '2025 BBB']


def load_merged_data():
    """Load the merged census data."""
    data_path = Path(DATA_FILE_PATH)
    
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
    """Filter data for United States level (level==3)."""
    logger.info("Filtering for United States data...")
    
    # Check what values are in the level and name columns
    logger.info(f"Unique values in 'level' column: {df['level'].unique()}")
    logger.info(f"Sample of name values: {df['name'].unique()[:10]}")
    
    # First try filtering by level==3
    us_data = df[df['level'] == 3].copy()
    
    logger.info(f"Found {len(us_data)} records with level==3")
    
    if len(us_data) == 0:
        logger.error("No US-level data found. Showing sample of all data:")
        print("\nSample of all data:")
        print(df[['year', 'name', 'level', GOV_PAYMENTS_COLUMN]].head(20))
        print(f"\nLevel value counts:")
        print(df['level'].value_counts())
        return None
    
    # Show what we found
    logger.info(f"Selected US data:")
    print(us_data[['year', 'name', 'level', GOV_PAYMENTS_COLUMN]].to_string())
    
    return us_data

def filter_corn_counties(df):
    """Filter data to only include counties that grew corn (> 0 acres)."""
    logger.info("Filtering for counties that grew corn...")
    
    # Check if corn_for_grain_acres column exists
    if 'corn_for_grain_acres' not in df.columns:
        logger.error("corn_for_grain_acres column not found in data")
        return None
    
    # Convert corn acres to numeric, handling any non-numeric values
    df['corn_for_grain_acres'] = pd.to_numeric(df['corn_for_grain_acres'], errors='coerce')
    
    # Filter for county-level data (level==1) with corn acres > 0
    corn_counties = df[(df['level'] == 1) & (df['corn_for_grain_acres'] > 0)].copy()
    
    logger.info(f"Found {len(corn_counties)} county records with corn acres > 0")
    logger.info(f"Original data: {len(df)} records")
    logger.info(f"Corn counties data: {len(corn_counties)} records")
    
    # Show sample of corn counties data
    if len(corn_counties) > 0:
        logger.info("Sample of corn counties data:")
        print(corn_counties[['year', 'name', 'level', GOV_PAYMENTS_COLUMN, 'corn_for_grain_acres']].head(10))
    
    return corn_counties

def create_time_series_plot(us_data, corn_counties_data):
    """Create a time series plot of government payments over time."""
    logger.info("Creating time series plot...")
    
    # Simply extract years and values from the long format data
    years = sorted([int(year) for year in us_data['year'].unique()])
    
    # Extract US-wide government payments (using real dollars)
    us_gov_payments = []
    for year in years:
        year_data = us_data[us_data['year'] == year]
        if len(year_data) > 0:
            gov_value = year_data[GOV_PAYMENTS_COLUMN].iloc[0]
            us_gov_payments.append(gov_value)
            logger.info(f"Year {year} (US): Gov Payments ${gov_value:.0f} (2017 dollars)")
        else:
            us_gov_payments.append(np.nan)
            logger.info(f"Year {year} (US): No data found")
    
    # Extract corn counties government payments (average across counties)
    corn_gov_payments = []
    corn_acres = []
    
    for year in years:
        if corn_counties_data is not None:
            year_data = corn_counties_data[corn_counties_data['year'] == year]
            if len(year_data) > 0:
                # Calculate average government payments across all corn counties for this year
                avg_gov_value = year_data[GOV_PAYMENTS_COLUMN].mean()
                total_corn_acres = year_data['corn_for_grain_acres'].sum() if 'corn_for_grain_acres' in year_data.columns else np.nan
                corn_gov_payments.append(avg_gov_value)
                corn_acres.append(total_corn_acres)
                logger.info(f"Year {year} (Corn Counties): Avg Gov Payments ${avg_gov_value:.0f} (2017 dollars), Total Corn Acres {total_corn_acres:,.0f}")
            else:
                corn_gov_payments.append(np.nan)
                corn_acres.append(np.nan)
                logger.info(f"Year {year} (Corn Counties): No data found")
        else:
            corn_gov_payments.append(np.nan)
            corn_acres.append(np.nan)
    
    # Set up the plot style
    plt.style.use('seaborn-v0_8')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Time series of government payments - both US and corn counties
    ax1.plot(years, us_gov_payments, marker='o', linewidth=2, markersize=8, color='#2E86AB', label='Entire US')
    ax1.plot(years, corn_gov_payments, marker='s', linewidth=2, markersize=8, color='#A23B72', label='Corn Counties Only')
    
    # Add vertical lines for farm bills
    for i, (year, label) in enumerate(zip(FARM_BILL_YEARS, FARM_BILL_LABELS)):
        if year >= min(years) and year <= max(years):
            ax1.axvline(x=year, color='gray', linestyle='--', alpha=0.7, linewidth=1.5)
            # Add label with slight offset to avoid overlap
            ax1.text(year, ax1.get_ylim()[1] * (0.95 - i * 0.05), label, 
                    rotation=90, verticalalignment='top', horizontalalignment='right',
                    fontsize=9, alpha=0.8, color='gray')
    
    ax1.set_title('Average Government Payments per Farm\nAgricultural Census 1992-2022', 
                  fontsize=14, fontweight='bold')
    ax1.set_xlabel('Census Year', fontsize=12)
    ax1.set_ylabel('Average Government Payments per Farm (2017 $s)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(years)
    ax1.legend()
    
    # Add value labels on points for US data
    for i, (year, value) in enumerate(zip(years, us_gov_payments)):
        if not pd.isna(value):
            ax1.annotate(f'${value:.0f}', 
                        (year, value), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontsize=9)
    
    # Add value labels on points for corn counties data
    for i, (year, value) in enumerate(zip(years, corn_gov_payments)):
        if not pd.isna(value):
            ax1.annotate(f'${value:.0f}', 
                        (year, value), 
                        textcoords="offset points", 
                        xytext=(0,-15), 
                        ha='center',
                        fontsize=9)
    
    # Plot 2: Corn acres over time
    ax2.plot(years, corn_acres, marker='s', linewidth=2, markersize=8, color='#A23B72')
    ax2.set_title('Total Corn for Grain Acres in the United States\nAgricultural Census 1992-2022', 
                  fontsize=14, fontweight='bold')
    ax2.set_xlabel('Census Year', fontsize=12)
    ax2.set_ylabel('Total Corn for Grain Acres', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(years)
    
    # Add value labels on points
    for i, (year, value) in enumerate(zip(years, corn_acres)):
        if not pd.isna(value):
            ax2.annotate(f'{value:,.0f}', 
                        (year, value), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontsize=10)
    
    plt.tight_layout()
    
    # Save the plot
    output_dir = Path(OUTPUT_DIR) / FIGS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_path = output_dir / PLOT_FILENAME
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    logger.info(f"Plot saved to: {plot_path}")
    
    plt.show()
    
    return years, us_gov_payments, corn_gov_payments, corn_acres

def create_noncons_time_series_plot(us_data, corn_counties_data):
    """Create: 'Average Government Payments per Farm (non-Conservation)' over time."""
    logger.info("Creating non-conservation time series plot...")

    target_col = 'gov_payments_noncons_real'
    if target_col not in us_data.columns or (corn_counties_data is not None and target_col not in corn_counties_data.columns):
        logger.error(f"{target_col} not found in data. Did you compute it?")
        return None

    years = sorted([int(y) for y in us_data['year'].dropna().unique()])

    # US series
    us_series = []
    for y in years:
        sub = us_data.loc[us_data['year'] == y, target_col]
        val = sub.iloc[0] if len(sub) else np.nan
        us_series.append(val)
        if not pd.isna(val):
            logger.info(f"Year {y} (US, non-cons): ${val:.0f}")

    # Corn-counties series (average across corn counties in that year)
    corn_series = []
    for y in years:
        if corn_counties_data is None:
            corn_series.append(np.nan)
            continue
        sub = corn_counties_data.loc[corn_counties_data['year'] == y, target_col]
        val = sub.mean() if len(sub) else np.nan
        corn_series.append(val)
        if not pd.isna(val):
            logger.info(f"Year {y} (Corn counties, non-cons avg): ${val:.0f}")

    # Plot (same style/labels as your first figure)
    plt.style.use('seaborn-v0_8')
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    ax.plot(years, us_series, marker='o', linewidth=2, markersize=8, color='#2E86AB', label='Entire US')
    ax.plot(years, corn_series, marker='s', linewidth=2, markersize=8, color='#A23B72', label='Corn Counties Only')

    # Farm bill verticals & labels
    for i, (yr, label) in enumerate(zip(FARM_BILL_YEARS, FARM_BILL_LABELS)):
        if years and (min(years) <= yr <= max(years)):
            ax.axvline(x=yr, color='gray', linestyle='--', alpha=0.7, linewidth=1.5)
            ax.text(yr, ax.get_ylim()[1]*(0.95 - i*0.05), label,
                    rotation=90, va='top', ha='right', fontsize=9, alpha=0.8, color='gray')

    ax.set_title('Average Government Payments per Farm (non-Conservation)\nAgricultural Census 1992–2022',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Census Year', fontsize=12)
    ax.set_ylabel('Average Government Payments per Farm (2017 $s)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(years)
    ax.legend()

    # Point labels
    for (y, v) in zip(years, us_series):
        if not pd.isna(v):
            ax.annotate(f'${v:.0f}', (y, v), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
    for (y, v) in zip(years, corn_series):
        if not pd.isna(v):
            ax.annotate(f'${v:.0f}', (y, v), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=9)

    plt.tight_layout()

    # Save
    output_dir = Path(OUTPUT_DIR) / FIGS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    noncons_plot_path = output_dir / "gov_payments_noncons_timeseries.png"
    plt.savefig(noncons_plot_path, dpi=300, bbox_inches='tight')
    logger.info(f"Non-conservation plot saved to: {noncons_plot_path}")

    plt.show()

    return years, us_series, corn_series



logger.info("Starting government payments analysis...")

# Load the merged data (already deflated)
df = load_merged_data()
if df is None:
    logger.error("Failed to load census data. Exiting.")
    exit(1)

# Make sure these exist and are numeric, then create non-conservation series
for col in ['gov_payments_avg_real', 'gov_payments_conservation_real']:
    if col not in df.columns:
        logger.error(f"Required column missing: {col}")
    else:
        df[col] = pd.to_numeric(df[col], errors='coerce')

df['gov_payments_noncons_real'] = df['gov_payments_avg_real'] - df['gov_payments_conservation_real']


# Normalize year column
df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')

# Filter for US data
us_data = filter_us_data(df)

# Filter for counties that grew corn (from original data, not US-level data)
corn_counties_data = filter_corn_counties(df)

# Create visualizations directly from the long format data
# Pass both US data and corn counties data to the plotting function
years, us_gov_payments, corn_gov_payments, corn_acres = create_time_series_plot(us_data, corn_counties_data)

years_nc, us_noncons, corn_noncons = create_noncons_time_series_plot(us_data, corn_counties_data)


# Additional analysis
logger.info("\nAdditional Analysis:")

# Show the actual data we're working with
logger.info(f"US-wide government payments by year (2017 dollars):")
for year, value in zip(years, us_gov_payments):
    if not pd.isna(value):
        logger.info(f"  {year}: ${value:,.0f}")
    else:
        logger.info(f"  {year}: Missing")

logger.info(f"Corn counties government payments by year (2017 dollars):")
for year, value in zip(years, corn_gov_payments):
    if not pd.isna(value):
        logger.info(f"  {year}: ${value:,.0f}")
    else:
        logger.info(f"  {year}: Missing")

logger.info(f"Total corn acres by year:")
for year, value in zip(years, corn_acres):
    if not pd.isna(value):
        logger.info(f"  {year}: {value:,.0f} acres")
    else:
        logger.info(f"  {year}: Missing")

# Calculate percentage changes for both US and corn counties
if len([v for v in us_gov_payments if not pd.isna(v)]) > 1:
    valid_values = [(year, value) for year, value in zip(years, us_gov_payments) if not pd.isna(value)]
    if len(valid_values) >= 2:
        first_year, first_value = valid_values[0]
        last_year, last_value = valid_values[-1]
        pct_change = ((last_value - first_value) / first_value) * 100
        logger.info(f"US-wide change from {first_year} to {last_year}: {pct_change:.1f}%")

if len([v for v in corn_gov_payments if not pd.isna(v)]) > 1:
    valid_values = [(year, value) for year, value in zip(years, corn_gov_payments) if not pd.isna(value)]
    if len(valid_values) >= 2:
        first_year, first_value = valid_values[0]
        last_year, last_value = valid_values[-1]
        pct_change = ((last_value - first_value) / first_value) * 100
        logger.info(f"Corn counties change from {first_year} to {last_year}: {pct_change:.1f}%")

logger.info("Analysis completed successfully!")

