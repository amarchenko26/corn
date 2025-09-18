#!/usr/bin/env python3
"""
Agricultural Census Data Collection Script

This script collects census data files from different years, filters for the corresponding variables, and merges them into one data file
into an interim folder.

Census years and corresponding folder mappings:
- DS0042: 1992
- DS0043: 1997  
- DS0044: 2002
- DS0045: 2007
- DS0047: 2012

Census years and corresponding variable names:
- 1992: 
        1 stateicp ICPSR state code
        2 counicp ICPSR county code
        3 name Name of area
        4 fips State/county FIPS code
        5 statefip State FIPS code
        6 counfip County FIPS code
        7 level County=1 state=2 USA=3

        8 flag010001 Flag for item010001
        9 item010001 Farms (number), 1992
        39 item010016 Harvested crop land (acres), 1992
        75 item010034 Net cash return from agricultural sales for the farm unit (see text), average per farm (dollars), 1992

        121 item010057 Corn for grain or seed (farms), 1992
        123 item010058 Corn for grain or seed (acres), 1992
        125 item010059 Corn for grain or seed (bu.), 1992
        127 item010060 Corn for silage or green chop (farms), 1992
        129 item010061 Corn for silage or green chop (acres), 1992
        131 item010062 Corn for silage/green chop (tons, green), 1992

        527 item040011 Gov payments-Total received, ($1,000), 1992
        529 item040012 Gov payments-Total received average per farm (dollars), 1992
        531 item040013 Gov payments-CRP & WRP, (farms), 1992
        533 item040014 Gov payments-CRP & WRP, ($1,000), 1992
        535 item040015 Gov payments-CRP & WRP avg/farm (dollars), 1992

        565 item040030 CCC Loan-Total (farms), 1992
        567 item040031 CCC Loan-Total ($1,000), 1992
        569 item040032 CCC Loan-Corn, (farms), 1992
        571 item040033 CCC Loan-Corn, ($1,000), 1992
        573 item040034 CCC Loan-Wheat, (farms), 1992
        575 item040035 CCC Loan-Wheat, ($1,000), 1992

        837 item060074 Land under Federal acreage reduction programs--Diverted under annual commodity programs, (farms), 1992
        839 item060075 Land under Federal acreage reduction programs--Diverted under annual commodity programs, (acres), 1992
        841 item060076 Land under Federal acreage reduction programs-- Conservation Reserve or Wetlands Reserve Programs (farms), 1992
        843 item060077 Land under Federal acreage reduction programs-- Conservation Reserve or Wetlands Reserve Programs, (acres), 1992

- 1997: 
        1 state State ICPSR code
        2 county County ICPSR code
        3 name Name of state/county
        4 level County=1 state=2 USA=3
        5 statefip State FIPS code
        6 counfip County FIPS code
        7 fips State/county FIPS 

        8 item01001 Farms (number), 1997
        24 item01017 Total cropland, harvested cropland (acres), 1997
        28 item01021 Market value of agricultural products sold, average per farm ($), 1997 
        42 item01035 Net cash return from ag sales for fm unit (see text) , average per farm ($), 1997
        260 item04003 Net cash return from ag sales for farm unit (see text) ,aver per farm ($), 1997 

        65 item01058 Corn for grain or seed (farms), 1997
        66 item01059 Corn for grain or seed (acres), 1997
        67 item01060 Corn for grain or seed (bushels), 1997
        68 item01061 Corn for silage or green chop (farms), 1997
        69 item01062 Corn for silage or green chop (acres), 1997
        70 item01063 Corn for silage or green chop (tons, green), 1997

        123 item02001 Market value of agricultural products sold, total sales (see text) (farms), 1997
        124 item02002 Market value of agricultural products sold, total sales (see text) ($1,000), 1997
        125 item02003 Market value of agricultural products sold, total sales, average per farm ($), 1997
        154 item02032 Sales by commodity/commodity group: Crops, incl nursery/greenhouse crops, grains, corn for grain (farms), 1997
        155 item02033 Sales by commodity/commodity group: Crops, incl nursery/greenhouse crops, grains, corn for grain ($1,000), 1997
        
        267 item04010 Government payments, total received (farms), 1997
        268 item04011 Government payments, total received ($1,000), 1997
        269 item04012 Government payments, total received, average per farm ($), 1997
        270 item04013 Govt pay, amount from Conservation Reserve/Wetlands Reserve Programs (farms), 1997
        271 item04014 Govt pay, amount from Conservation Reserve/Wetlands Reserve Program ($1,000), 1997
        272 item04015 Gov pay, amount from Conservation Res/Wetlands Res Program, average per farm ($), 1997

        287 item04030 Commodity Credit Corporation Loans - Total (farms), 1997
        288 item04031 Commodity Credit Corporation Loans - Total ($1,000), 1997
        289 item04032 Commodity Credit Corporation Loans - Corn (farms), 1997
        290 item04033 Commodity Credit Corporation Loans - Corn ($1,000), 1997
        291 item04034 Commodity Credit Corporation Loans - Wheat (farms), 1997
        292 item04035 Commodity Credit Corporation Loans - Wheat ($1,000), 1997

            750 item12101 Government payments-Total received (farms), 1997
            751 item12102 Government payments-Total received ($1,000), 1997
            752 item12103 Government payments-Total received, average per farm ($), 1997
            753 item12104 Government payments-Amount from Conservation Reserve/Wetlands Reserve Programs (farms), 1997
            754 item12105 Government payments-Amount from Conservation Reserve/Wetlands Reserve Programs ($1,000), 1997
            755 item12106 Government payments-Amount from Conservation Reserve/Wetlands Reserve Program, average per farm ($), 1997

            874 item12225 Corn for grain or seed (farms), 1997
            875 item12226 Corn for grain or seed (acres), 1997
            876 item12227 Corn for grain or seed (bushels), 1997
            877 item12228 Corn for silage or green chop (farms), 1997
            878 item12229 Corn for silage or green chop (acres), 1997
            879 item12230 Corn for silage or green chop (tons, green), 1997

- 2002: 
        1 state ICPSR state code
        2 county ICPSR county code
        3 level 1=county 2=state 3=USA
        4 fips State\county FIPS code
        5 statefip State FIPS code
        6 counfip County FIPS code
        7 name Name of area

        8 item01001 Farms (number, 2002)
        24 item01017 Total crop land, Harvested crop land (acres, 2002)
        28 item01021 Market value of agricultural products sold (see text), Average per farm (dollars, 2002)

        69 item01062 Selected crops harvested, Corn for grain (farms, 2002)
        70 item01063 Selected crops harvested, Corn for grain (acres, 2002)
        71 item01064 Selected crops harvested, Corn for grain (bushels)
        72 item01065 Selected crops harvested, Corn for silage or greenchop (farms, 2002)
        73 item01066 Selected crops harvested, Corn for silage or greenchop (acres, 2002)
        77 item01067 Selected crops harvested, Corn for silage or greenchop (tons, 2002)

        384 item05001 Government payments, Total received (farms, 2002)
        385 item05002 Government payments, Total received (farms, 1997)
        386 item05003 Government payments, Total received ($1,000, 2002)
        387 item05004 Government payments, Total received ($1,000, 1997)
        388 item05005 Government payments, Total received, Average per farm (dollars, 2002)
        389 item05006 Government payments, Total received, Average per farm (dollars, 1997)
        390 item05007 Government payments, Total received, Amount from Conservation Reserve & Wetlands Reserve Programs (farms, 2002)
        391 item05008 Government payments, Total received, Amount from Conservation Reserve & Wetlands Reserve Programs (farms, 1997)
        392 item05009 Government payments, Total received, Amount from Conservation Reserve & Wetlands Reserve Programs ($1,000, 2002)
        393 item05010 Government payments, Total received, Amount from Conservation Reserve & Wetlands Reserve Programs ($1,000, 1997)
        394 item05011 Government payments, Total received, Amount from Conservation Reserve & Wetlands Reserve Programs, Average per farm (dollars, 2002)
        395 item05012 Government payments, Total received, Amount from Conservation Reserve & Wetlands Reserve Programs, Average per farm (dollars, 1997)
        396 item05013 Government payments, Total received, Amount from other federal farm programs (farms, 2002)
        397 item05014 Government payments, Total received, Amount from other federal farm programs (farms, 1997)
        398 item05015 Government payments, Total received, Amount from other federal farm programs ($1,000, 2002)
        399 item05016 Government payments, Total received, Amount from other federal farm programs ($1,000, 1997)
        400 item05017 Government payments, Total received, Amount from other federal farm programs, Average per farm (dollars, 2002)
        401 item05018 Government payments, Total received, Amount from other federal farm programs, Average per farm (dollars, 1997)
        402 item05019 Commodity Credit Corporation loans, Total (farms, 2002)
        404 item05021 Commodity Credit Corporation loans, Total ($1,000, 2002)

- 2007: 
        1 state State ICPSR code
        2 statefip State FIPS code
        3 county County ICPSR code
        4 countyfip County FIPS code
        5 name Name of state/county
        6 fips FIPS code
        7 level County=1 state=2 USA=3
        8 data1_1 Farms (number)

        69 data1_62 Selected crops harvested\Corn for grain (farms)
        70 data1_63 Selected crops harvested\Corn for grain (acres)
        71 data1_64 Selected crops harvested\Corn for grain (bushels)
        72 data1_65 Selected crops harvested\Corn for silage or greenchop (farms)
        73 data1_66 Selected crops harvested\Corn for silage or greenchop (acres)
        74 data1_67 Selected crops harvested\Corn for silage or greenchop (tons)

        422 data5_1 Government payments\Total received (farms, 2007)
        423 data5_2 Government payments\Total received (farms, 2002)
        424 data5_3 Government payments\Total received ($1,000, 2007)
        425 data5_4 Government payments\Total received ($1,000, 2002)
        426 data5_5 Government payments\Total received\Average per farm (dollars, 2007)
        427 data5_6 Government payments\Total received\Average per farm (dollars, 2002)
        428 data5_7 Government payments\Total received\Amount from Conservation Reserve, Wetlands Reserve, Farmable Wetlands, & Conservation Reserve Enhancement Programs 2002 (farms, 2007)
        429 data5_8 Government payments\Total received\Amount from conservation reserve, wetlands reserve, farmable wetlands, & conservation reserve enhancement programs 2002 (farms, 2002)
        430 data5_9 Government payments\Total received\Amount from conservation reserve, wetlands reserve, farmable wetlands, & conservation reserve enhancement programs 2002 ($1,000, 2007)
        431 data5_10 Government payments\Total received\Amount from conservation reserve, wetlands reserve, farmable wetlands, & conservation reserve enhancement programs 2002 ($1,000, 2002)
        432 data5_11 Government payments\Total received\Amount from conservation reserve, wetlands reserve, farmable wetlands, & conservation reserve enhancement programs 2002\Average per farm (dollars, 2007)
        433 data5_12 Government payments\Total received\Amount from conservation reserve, wetlands reserve, farmable wetlands, & conservation reserve enhancement programs 2002\Average per farm (dollars, 2002)
        434 data5_13 Government payments\Total received\Amount from other federal farm programs (farms, 2007)
        435 data5_14 Government payments\Total received\Amount from other federal farm programs (farms, 2002)
        436 data5_15 Government payments\Total received\Amount from other federal farm programs ($1,000, 2007)
        437 data5_16 farm programs ($1,000, 2007) Government payments\Total received\Amount from other federal farm programs ($1,000, 2002)
        438 data5_17 Government payments\Total received\Amount from other federal farm programs\Average per farm (dollars, 2007)
        439 data5_18 Government payments\Total received\Amount from other federal farm programs\Average per farm (dollars, 2002)
        440 data5_19 Commodity credit corporation loans\Total (farms, 2007)
        441 data5_20 Commodity credit corporation loans\Total (farms, 2002)
        442 data5_21 Commodity credit corporation loans\Total ($1,000, 2007)
        443 data5_22 Commodity credit corporation loans\Total ($1,000, 2002)

- 2012: 
        1 stateicp State ICPSR code
        2 counicp County ICPSR code
        3 name Name of geographic area
        4 level County=1 state=2 USA=3
        5 fips State/county FIPS code
        6 statefip State FIPS code
        7 cofips County FIPS code
        8 data1_1 Farms (number)

        70 data1_63 Selected crops harvested\Corn for grain (farms)
        71 data1_64 Selected crops harvested\Corn for grain (acres)
        72 data1_65 Selected crops harvested\Corn for grain (bushels)
        73 data1_66 Selected crops harvested\Corn for silage or greenchop (farms)
        74 data1_67 Selected crops harvested\Corn for silage or greenchop (acres)
        75 data1_68 Selected crops harvested\Corn for silage or greenchop (tons)

        439 data5_1 Government payments\Total received (farms, 2012)
        440 data5_2 Government payments\Total received (farms, 2007)
        441 data5_3 Government payments\Total received ($1,000, 2012)
        442 data5_4 Government payments\Total received ($1,000, 2007)
        443 data5_5 Government payments\Total received\average per farm ($, 2012)
        444 data5_6 Government payments\Total received\average per farm ($, 2007)
        445 data5_7 Government payments\Total received\Amount from conservation reserve, wetlands reserve & conservation reserve enhancement programs 2007 (farms, 2012)
        446 data5_8 Government payments\Total received\Amount from conservation reserve, wetlands reserve  & conservation reserve enhancement programs 2007 (farms, 2007)
        447 data5_9 Government payments\Total received\Amount from conservation reserve, wetlands reserve & conservation reserve enhancement programs 2007 ($1,000, 2012)
        448 data5_10 Government payments\Total received\Amount from conservation reserve, wetlands reserve & conservation reserve enhancement programs 2007 ($1,000, 2007)
        449 data5_11 Government payments\Total received\Amount from conservation reserve, wetlands reserve & conservation reserve enhancement programs 2007\Average per farm ($, 2012)
        450 data5_12 Government payments\Total received\Amount from conservation reserve, wetlands reserve & conservation reserve enhancement programs 2007\Average per farm ($, 2007)
        451 data5_13 Government payments\Total received\Amount from other federal farm programs (farms, 2012)
        452 data5_14 Government payments\Total received\Amount from other federal farm programs (farms, 2007)
        453 data5_15 Government payments\Total received\Amount from other federal farm programs ($1,000, 2012)
        454 data5_16 Government payments\Total received\Amount from other federal farm programs ($1,000, 2007)
        455 data5_17 Government payments\Total received\Amount from other federal farm programs\Average per farm ($, 2012)
        456 data5_18 Government payments\Total received\Amount from other federal farm programs\Average per farm ($, 2007)
        457 data5_19 Commodity credit corporation loans\Total (farms, 2012)
        458 data5_20 Commodity credit corporation loans\Total (farms, 2007)
        459 data5_21 Commodity credit corporation loans\Total ($1,000, 2012)
        460 data5_22 Commodity credit corporation loans\Total ($1,000, 2007)
        462 data5_24 Commodity credit corporation loans\Total\Amount spent to repay CCC loans (farms, 2007)
        463 data5_25 Commodity credit corporation loans\Total\Amount spent to repay CCC loans ($1,000, 2012)
        464 data5_26 Commodity credit corporation loans\Total\Amount spent to repay CCC loans ($1,000, 2007)

- 2017:

    'GOVT PROGRAMS, FEDERAL - RECEIPTS, MEASURED IN $ / OPERATION'
    'GOVT PROGRAMS, FEDERAL, (EXCL CONSERVATION & WETLANDS) - RECEIPTS, MEASURED IN $ / OPERATION'
    'INCOME, FARM-RELATED, GOVT PROGRAMS, STATE & LOCAL - RECEIPTS, MEASURED IN $ / OPERATION'

2025-09-18 15:17:21,716 - INFO - All government related SHORT_DESC values in NASS 2017: ['GOVT PROGRAMS, FEDERAL - RECEIPTS, MEASURED IN $ / OPERATION', 'GOVT PROGRAMS, FEDERAL - OPERATIONS WITH RECEIPTS', 'GOVT PROGRAMS, FEDERAL - RECEIPTS, MEASURED IN $', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - ACRES', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - NUMBER OF OPERATIONS', 'INCOME, FARM-RELATED, GOVT PROGRAMS, STATE & LOCAL - OPERATIONS WITH RECEIPTS', 'INCOME, FARM-RELATED, GOVT PROGRAMS, STATE & LOCAL - RECEIPTS, MEASURED IN $', 'INCOME, FARM-RELATED, GOVT PROGRAMS, STATE & LOCAL - RECEIPTS, MEASURED IN $ / OPERATION', 'GOVT PROGRAMS, FEDERAL, (EXCL CONSERVATION & WETLANDS) - RECEIPTS, MEASURED IN $', 'GOVT PROGRAMS, FEDERAL, (EXCL CONSERVATION & WETLANDS) - RECEIPTS, MEASURED IN $ / OPERATION', 'GOVT PROGRAMS, FEDERAL, (EXCL CONSERVATION & WETLANDS) - OPERATIONS WITH RECEIPTS', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - RECEIPTS, MEASURED IN $', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - RECEIPTS, MEASURED IN $ / OPERATION', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - OPERATIONS WITH RECEIPTS', 'COMMODITY TOTALS, INCL GOVT PROGRAMS - RECEIPTS, MEASURED IN $', 'COMMODITY TOTALS, INCL GOVT PROGRAMS - RECEIPTS, MEASURED IN $ / OPERATION', 'COMMODITY TOTALS, INCL GOVT PROGRAMS - OPERATIONS WITH RECEIPTS']


- 2022: 

    'GOVT PROGRAMS, FEDERAL - RECEIPTS, MEASURED IN $ / OPERATION'
    'GOVT PROGRAMS, FEDERAL, (EXCL CONSERVATION & WETLANDS) - RECEIPTS, MEASURED IN $ / OPERATION'
    'INCOME, FARM-RELATED, GOVT PROGRAMS, STATE & LOCAL - RECEIPTS, MEASURED IN $ / OPERATION'

 All government related SHORT_DESC values in NASS 2022: ['COMMODITY TOTALS, INCL GOVT PROGRAMS - OPERATIONS WITH RECEIPTS', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - NUMBER OF OPERATIONS', 'INCOME, FARM-RELATED, GOVT PROGRAMS, STATE & LOCAL - OPERATIONS WITH RECEIPTS', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - ACRES', 'COMMODITY TOTALS, INCL GOVT PROGRAMS - RECEIPTS, MEASURED IN $ / OPERATION', 'GOVT PROGRAMS, FEDERAL - RECEIPTS, MEASURED IN $', 'GOVT PROGRAMS, FEDERAL, (EXCL CONSERVATION & WETLANDS) - RECEIPTS, MEASURED IN $', 'GOVT PROGRAMS, FEDERAL - OPERATIONS WITH RECEIPTS', 'COMMODITY TOTALS, INCL GOVT PROGRAMS - RECEIPTS, MEASURED IN $', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - OPERATIONS WITH RECEIPTS', 'INCOME, FARM-RELATED, GOVT PROGRAMS, STATE & LOCAL - RECEIPTS, MEASURED IN $', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - RECEIPTS, MEASURED IN $', 'GOVT PROGRAMS, FEDERAL - RECEIPTS, MEASURED IN $ / OPERATION', 'GOVT PROGRAMS, FEDERAL, (EXCL CONSERVATION & WETLANDS) - RECEIPTS, MEASURED IN $ / OPERATION', 'GOVT PROGRAMS, FEDERAL, (EXCL CONSERVATION & WETLANDS) - OPERATIONS WITH RECEIPTS', 'GOVT PROGRAMS, FEDERAL, CONSERVATION & WETLANDS - RECEIPTS, MEASURED IN $ / OPERATION', 'INCOME, FARM-RELATED, GOVT PROGRAMS, STATE & LOCAL - RECEIPTS, MEASURED IN $ / OPERATION']


"""

import os
import shutil
import pandas as pd
from pathlib import Path
import logging
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Choose which columns to deflate to real dollars 
DEFLATABLE_COLS = ['gov_payments_avg']

# Additional census files (2017-2022 NASS format)
NASS_2017_FILE = "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/raw/NASS_2017-2022/qs.census2017.txt"
NASS_2022_FILE = "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/raw/NASS_2017-2022/qs.census2022.txt"

# Variable mapping configuration
# Define which variables to extract and their locations in each data source
VARIABLE_MAPPING = {
    'gov_payments_avg': {
        'icpsr_columns': {
            1992: 'item040012',  # Gov payments-Total received average per farm (dollars), 1992
            1997: 'item04012',   # Government payments, total received, average per farm ($), 1997
            2002: 'item05005',   # Government payments, Total received, Average per farm (dollars, 2002)
            2007: 'data5_5',     # Government payments\Total received\Average per farm (dollars, 2007)
            2012: 'data5_5',     # Government payments\Total received\average per farm ($, 2012)
        },
        'nass_short_desc': 'GOVT PROGRAMS, FEDERAL - RECEIPTS, MEASURED IN $ / OPERATION',
        'description': 'Government payments average per farm'
    },
    'corn_for_grain_acres': {
        'icpsr_columns': {
            1992: 'item010058',  # Corn for grain or seed (acres), 1992
            1997: 'item01059',   # Corn for grain or seed (acres), 1997
            2002: 'item01063',   # Selected crops harvested, Corn for grain (acres, 2002)
            2007: 'data1_63',    # Selected crops harvested\Corn for grain (acres)
            2012: 'data1_64',    # Selected crops harvested\Corn for grain (acres)
        },
        'nass_short_desc': 'CORN, GRAIN - ACRES HARVESTED',
        'description': 'Corn for grain acres harvested'
    }
    # Add more variables here as needed
    # 'market_value_avg': {
    #     'icpsr_columns': {
    #         1992: 'item010034',  # Net cash return from agricultural sales for the farm unit
    #         # ... etc
    #     },
    #     'nass_short_desc': 'MARKET VALUE OF AGRICULTURAL PRODUCTS SOLD - RECEIPTS, MEASURED IN $ / OPERATION',
    #     'description': 'Market value of agricultural products sold per farm'
    # }
}



def setup_directories():
    """Create interim directory structure if it doesn't exist."""
    interim_dir = Path("/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/interim")
    interim_dir.mkdir(exist_ok=True)
    
    # Create year subdirectories for all census years
    years = [1992, 1997, 2002, 2007, 2012, 2017, 2022]
    for year in years:
        year_dir = interim_dir / str(year)
        year_dir.mkdir(exist_ok=True)
        logger.info(f"Created directory: {year_dir}")
    
    return interim_dir
    

def load_nass_census_data(file_path, year):
    """Load NASS census data and explore government payment descriptions."""
    logger.info(f"Loading NASS census data for {year} from {file_path}")
    
    try:
        # Load the data
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        logger.info(f"Loaded NASS {year} data: {len(df)} rows, {len(df.columns)} columns")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading NASS {year} data: {e}")
        return None

def process_nass_census_data(df, year):
    """
    Minimal processor for NASS 2017/2022:
      - DOMAIN_DESC == 'TOTAL' only
      - exact SHORT_DESC match using VARIABLE_MAPPING[var]['nass_short_desc']
      - cleans VALUE: (D)/(H)/(NA)/(Z) -> NaN; remove $ and commas
      - maps by level to columns named by VARIABLE_MAPPING keys
    """
    logger.info(f"Processing NASS {year} data (minimal TOTAL-domain pipeline)")

    # --- helpers ---
    def norm(s):
        return s.astype(str).str.strip().str.upper()

    def clean_value(s):
        s = s.astype(str).str.strip()
        s = s.where(~s.isin(['(D)', '(H)', '(NA)', '(Z)']))
        s = s.str.replace(r'[\$,]', '', regex=True)
        return pd.to_numeric(s, errors='coerce')

    # normalize a few text cols used below (only if present)
    for col in ['AGG_LEVEL_DESC','SHORT_DESC','DOMAIN_DESC',
                'STATE_NAME','COUNTY_NAME','COUNTRY_NAME',
                'UNIT_DESC']:
        if col in df.columns:
            df[col] = norm(df[col])

    # zero-pad FIPS used in keys
    if 'STATE_FIPS_CODE' in df.columns:
        df['STATE_FIPS_CODE'] = df['STATE_FIPS_CODE'].astype(str).str.zfill(2)
    if 'COUNTY_CODE' in df.columns:
        df['COUNTY_CODE'] = df['COUNTY_CODE'].astype(str).str.zfill(3)

    # 1) TOTAL domain only
    if 'DOMAIN_DESC' in df.columns:
        df = df[df['DOMAIN_DESC'] == 'TOTAL'].copy()

    # 2) limit to levels we support
    level_map = {'COUNTY': 1, 'STATE': 2, 'NATIONAL': 3}
    df = df[df['AGG_LEVEL_DESC'].isin(level_map.keys())].copy()
    df['level'] = df['AGG_LEVEL_DESC'].map(level_map)

    out_frames = []

    for lvl_name, lvl_num in level_map.items():
        sub = df[df['AGG_LEVEL_DESC'] == lvl_name]
        if sub.empty:
            continue

        # base geography frame
        if lvl_name == 'COUNTY':
            base = (sub[['YEAR','COUNTY_NAME','STATE_FIPS_CODE','COUNTY_CODE','level']]
                    .drop_duplicates()
                    .rename(columns={'YEAR':'year','COUNTY_NAME':'name',
                                     'STATE_FIPS_CODE':'statefip','COUNTY_CODE':'counfip'}))
            make_bkey = lambda b: b['name'] + '_' + b['statefip'] + '_' + b['counfip']
            make_key  = lambda d: d['COUNTY_NAME'] + '_' + d['STATE_FIPS_CODE'] + '_' + d['COUNTY_CODE']
        elif lvl_name == 'STATE':
            base = (sub[['YEAR','STATE_NAME','STATE_FIPS_CODE','level']]
                    .drop_duplicates()
                    .rename(columns={'YEAR':'year','STATE_NAME':'name','STATE_FIPS_CODE':'statefip'}))
            base['counfip'] = np.nan
            make_bkey = lambda b: b['name'] + '_' + b['statefip']
            make_key  = lambda d: d['STATE_NAME'] + '_' + d['STATE_FIPS_CODE']
        else:  # NATIONAL
            base = (sub[['YEAR','COUNTRY_NAME','level']]
                    .drop_duplicates()
                    .rename(columns={'YEAR':'year','COUNTRY_NAME':'name'}))
            base['statefip'] = np.nan
            base['counfip'] = np.nan
            make_bkey = lambda b: b['name']
            make_key  = lambda d: d['COUNTRY_NAME']

        # for each requested variable, match by SHORT_DESC and map into base
        for var_name, cfg in VARIABLE_MAPPING.items():
            short = cfg.get('nass_short_desc')
            if not short:
                continue
            target_short = str(short).strip().upper()

            rows = sub[sub['SHORT_DESC'] == target_short].copy()
            if rows.empty or 'VALUE' not in rows.columns:
                base[var_name] = np.nan
                continue

            rows['VALNUM'] = clean_value(rows['VALUE'])
            kmap = dict(zip(make_key(rows), rows['VALNUM']))
            base[var_name] = make_bkey(base).map(kmap)

        # drop rows where all requested vars are NaN
        wanted_cols = list(VARIABLE_MAPPING.keys())
        base = base.dropna(subset=[c for c in wanted_cols if c in base.columns], how='all')

        if not base.empty:
            out_frames.append(base)

    result = pd.concat(out_frames, ignore_index=True) if out_frames else pd.DataFrame()
    if result.empty:
        logger.warning(f"No usable rows found for NASS {year} with DOMAIN=='TOTAL' after simple mapping.")
    else:
        keep_cols = ['year','name','level','statefip','counfip'] + [c for c in VARIABLE_MAPPING.keys() if c in result.columns]
        logger.info(f"NASS {year} processed rows: {len(result)} | cols: {len(keep_cols)}")
        logger.info(result[keep_cols].head().to_string())
        result = result[keep_cols]
    return result


def load_deflator_data():
    """Load the price deflator data."""
    deflator_path = Path("/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/raw/deflator/price_index_A191RG_BEA.csv")
    
    if not deflator_path.exists():
        logger.error(f"Deflator file not found: {deflator_path}")
        return None
    
    try:
        deflator_df = pd.read_csv(deflator_path)
        logger.info(f"Loaded deflator data: {len(deflator_df)} rows")
        
        # Extract year from observation_date
        deflator_df['year'] = pd.to_datetime(deflator_df['observation_date']).dt.year
        
        # Rename the deflator column for clarity
        deflator_df = deflator_df.rename(columns={'A191RG3A086NBEA': 'price_deflator'})
        
        # Keep only year and deflator columns
        deflator_df = deflator_df[['year', 'price_deflator']].copy()
        
        logger.info(f"Deflator data years: {deflator_df['year'].min()} to {deflator_df['year'].max()}")
        return deflator_df
    except Exception as e:
        logger.error(f"Error loading deflator data: {e}")
        return None

def deflate_columns(df, deflator_df, DEFLATABLE_COLS):
    """Deflate specified columns using the price deflator."""
    logger.info("Deflating monetary columns to 2017 dollars...")
    
    # Merge the deflator data with the main dataframe
    df_with_deflator = df.merge(deflator_df, on='year', how='left')
    
    # Check if we have deflator data for all years
    missing_deflator = df_with_deflator['price_deflator'].isna().sum()
    if missing_deflator > 0:
        logger.warning(f"Missing deflator data for {missing_deflator} records")
        missing_years = df_with_deflator[df_with_deflator['price_deflator'].isna()]['year'].unique()
        logger.info(f"Missing years: {missing_years}")
    
    # Deflate each specified column
    for col in DEFLATABLE_COLS:
        if col in df_with_deflator.columns:
            # Clean the column data first (remove $, commas, etc.)
            df_with_deflator[col] = (
                df_with_deflator[col]
                .astype(str)
                .str.replace(r'[^\d\.\-]', '', regex=True)  # remove $ , spaces, etc.
                .replace('', np.nan)
                .astype(float)
            )
            
            # Create deflated column name
            real_col_name = f"{col}_real"
            
            # Calculate real values (in 2017 dollars)
            # Formula: real_value = nominal_value * (100 / deflator_value)
            df_with_deflator[real_col_name] = (
                df_with_deflator[col] * 
                (100 / df_with_deflator['price_deflator'])
            )
            
            logger.info(f"Created deflated column: {real_col_name}")
        else:
            logger.warning(f"Column {col} not found in data, skipping deflation")
    
    logger.info("Deflation completed. Added real dollar columns (2017 base year).")
    
    # Show some examples of the deflation
    sample_cols = ['year'] + [col for col in DEFLATABLE_COLS if col in df_with_deflator.columns] + [f"{col}_real" for col in DEFLATABLE_COLS if col in df_with_deflator.columns]
    sample_data = df_with_deflator[sample_cols].dropna().head()
    if len(sample_data) > 0:
        logger.info("Sample of deflated data:")
        logger.info(sample_data.to_string())
    
    return df_with_deflator

def get_icpsr_variable_mapping(year):
    """Get variable mapping for ICPSR data for a specific year."""
    # Base mapping for all years
    base_mapping = {
        'name': 'name',
        'level': 'level',
        'fips': 'fips',
        'statefip': 'statefip',
        'counfip': 'counfip'
    }
    
    # Add variable-specific columns for this year
    for var_name, var_config in VARIABLE_MAPPING.items():
        if year in var_config['icpsr_columns']:
            base_mapping[var_name] = var_config['icpsr_columns'][year]
    
    # Handle special cases for different years
    if year == 2007:
        base_mapping['counfip'] = 'countyfip'
    elif year == 2012:
        base_mapping['counfip'] = 'cofips'
    
    return base_mapping

def filter_and_process_data(file_path, year, variable_mapping):
    """Filter data to keep only specified variables and add year column."""
    try:
        # Read the TSV file
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        logger.info(f"Loaded {len(df)} rows from {file_path}")
        
        # Create case-insensitive column mapping
        df_columns_lower = {col.lower(): col for col in df.columns}
        logger.info(f"Available columns in {year}: {list(df.columns)[:10]}...")  # Show first 10 columns
        
        # Select only the variables we need (case-insensitive)
        required_vars = list(variable_mapping.values())
        available_vars = []
        missing_vars = []
        
        for var in required_vars:
            var_lower = var.lower()
            if var_lower in df_columns_lower:
                actual_col_name = df_columns_lower[var_lower]
                available_vars.append(actual_col_name)
            else:
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"Missing variables in {year}: {missing_vars}")
            logger.info(f"Looking for columns containing 'item' or 'data': {[col for col in df.columns if 'item' in col.lower() or 'data' in col.lower()][:10]}")
        
        if not available_vars:
            logger.error(f"No required variables found in {year}")
            return None
        
        # Filter dataframe to only include available variables
        df_filtered = df[available_vars].copy()
        
        # Create mapping from actual column names to our standard names
        actual_to_standard = {}
        for standard_name, original_var in variable_mapping.items():
            original_var_lower = original_var.lower()
            if original_var_lower in df_columns_lower:
                actual_col_name = df_columns_lower[original_var_lower]
                actual_to_standard[actual_col_name] = standard_name
        
        # Rename columns to consistent names
        df_filtered = df_filtered.rename(columns=actual_to_standard)
        
        # Add year column
        df_filtered['year'] = year
        
        # Reorder columns to have year first
        cols = ['year'] + [col for col in df_filtered.columns if col != 'year']
        df_filtered = df_filtered[cols]
        
        logger.info(f"Filtered to {len(df_filtered)} rows with {len(df_filtered.columns)} columns")
        return df_filtered
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None

def collect_census_files():
    """Collect census files from different years, filter variables, and create merged dataset."""
    
    # Define the base path and folder mappings
    base_path = Path("/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/raw/ICPSR_1850-2012")
    
    # Folder to year mapping
    folder_year_mapping = {
        "DS0042": 1992,
        "DS0043": 1997,
        "DS0044": 2002,
        "DS0045": 2007,
        "DS0047": 2012
    }
    
    # Folder to file number mapping (for correct file naming)
    folder_file_mapping = {
        "DS0042": "0042",
        "DS0043": "0043", 
        "DS0044": "0044",
        "DS0045": "0045",
        "DS0047": "0047"
    }
        
    # Load deflator data
    deflator_df = load_deflator_data()
    if deflator_df is None:
        logger.error("Failed to load deflator data. Exiting.")
        return [], [{'error': 'Failed to load deflator data'}]
    
    # Get list of columns to deflate
    logger.info(f"Columns to deflate: {DEFLATABLE_COLS}")
    
    # Set up interim directories
    interim_dir = setup_directories()
    
    collected_files = []
    missing_files = []
    processed_dataframes = []
    
    for folder, year in folder_year_mapping.items():
        logger.info(f"Processing {folder} (Year: {year})")
        
        # Construct the source file path
        file_number = folder_file_mapping[folder]
        source_file = base_path / folder / f"35206-{file_number}-Data.tsv"
        
        if source_file.exists():
            try:
                # Get variable mapping for this year
                variable_mapping = get_icpsr_variable_mapping(year)
                
                # Process and filter the data
                df_filtered = filter_and_process_data(source_file, year, variable_mapping)
                
                if df_filtered is not None:
                    # Save individual year file
                    year_file = interim_dir / str(year) / f"census_{year}_filtered.tsv"
                    df_filtered.to_csv(year_file, sep='\t', index=False)
                    
                    # Add to list for merging
                    processed_dataframes.append(df_filtered)
                    
                    collected_files.append({
                        'year': year,
                        'folder': folder,
                        'source': str(source_file),
                        'destination': str(year_file),
                        'rows': len(df_filtered),
                        'columns': len(df_filtered.columns)
                    })
                    logger.info(f"✓ Processed {source_file.name} → {year_file.name} ({len(df_filtered)} rows, {len(df_filtered.columns)} cols)")
                else:
                    missing_files.append({'folder': folder, 'year': year, 'error': 'Failed to process data'})
                    
            except Exception as e:
                logger.error(f"✗ Failed to process {source_file}: {e}")
                missing_files.append({'folder': folder, 'year': year, 'error': str(e)})
        else:
            logger.warning(f"✗ File not found: {source_file}")
            missing_files.append({'folder': folder, 'year': year, 'error': 'File not found'})
    
    # Create merged dataset
    if processed_dataframes:
        logger.info("Creating merged dataset...")
        merged_df = pd.concat(processed_dataframes, ignore_index=True)
        
        # Apply deflation to the merged dataset
        logger.info("Applying deflation to merged dataset...")
        merged_df_deflated = deflate_columns(merged_df, deflator_df, DEFLATABLE_COLS)
        
        # Create final dataset with only deflated columns (plus essential identifiers)
        essential_columns = ['year', 'name', 'level', 'fips', 'statefip', 'counfip', 'corn_for_grain_acres']
        real_columns = [f"{col}_real" for col in DEFLATABLE_COLS if f"{col}_real" in merged_df_deflated.columns]
        
        # Combine essential columns with deflated columns
        final_columns = essential_columns + real_columns
        available_final_columns = [col for col in final_columns if col in merged_df_deflated.columns]
        
        final_df = merged_df_deflated[available_final_columns].copy()
        
        # Save final dataset with deflated values
        final_file = interim_dir / "census_merged_1992_2012_deflated.tsv"
        final_df.to_csv(final_file, sep='\t', index=False)
        
        logger.info(f"✓ Created deflated merged dataset: {final_file} ({len(final_df)} rows, {len(final_df.columns)} cols)")
        logger.info(f"Final columns: {list(final_df.columns)}")
        
        # Also save the full dataset with both nominal and real values for reference
        full_file = interim_dir / "census_merged_1992_2012_full.tsv"
        merged_df_deflated.to_csv(full_file, sep='\t', index=False)
        
        logger.info(f"✓ Created full dataset (nominal + real): {full_file} ({len(merged_df_deflated)} rows, {len(merged_df_deflated.columns)} cols)")
        
        # Add merged file info
        collected_files.append({
            'year': 'merged_deflated',
            'folder': 'all',
            'source': 'multiple',
            'destination': str(final_file),
            'rows': len(final_df),
            'columns': len(final_df.columns)
        })
        
        collected_files.append({
            'year': 'merged_full',
            'folder': 'all',
            'source': 'multiple',
            'destination': str(full_file),
            'rows': len(merged_df_deflated),
            'columns': len(merged_df_deflated.columns)
        })
    
    return collected_files, missing_files

def print_summary(collected_files, missing_files):
    """Print a summary of the collection process."""
    print("\n" + "="*80)
    print("AGRICULTURAL CENSUS DATA PROCESSING SUMMARY")
    print("="*80)
    
    if collected_files:
        print(f"\n✓ Successfully processed {len([f for f in collected_files if f['year'] != 'merged'])} year files:")
        total_rows = 0
        for file_info in collected_files:
            if file_info['year'] != 'merged':
                print(f"  {file_info['year']}: {file_info['rows']} rows, {file_info['columns']} columns")
                print(f"    → {file_info['destination']}")
                total_rows += file_info['rows']
        
        # Show merged file info
        merged_files = [f for f in collected_files if f['year'] in ['merged_deflated', 'merged_full']]
        if merged_files:
            print(f"\n✓ Created merged datasets:")
            for merged_file in merged_files:
                file_type = "deflated (real dollars)" if merged_file['year'] == 'merged_deflated' else "full (nominal + real)"
                print(f"  {file_type}: {merged_file['rows']} total rows, {merged_file['columns']} columns")
                print(f"    → {merged_file['destination']}")
    
    if missing_files:
        print(f"\n✗ {len(missing_files)} files could not be processed:")
        for file_info in missing_files:
            print(f"  {file_info['year']} ({file_info['folder']}): {file_info['error']}")
    
    print(f"\nOutput directory: /Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/interim")
    print("="*80)


def process_nass_data():
    """Process NASS census data and convert to ICPSR format."""
    logger.info("Processing NASS census data...")
    
    processed_nass_data = []
    
    # Process 2017 data
    df_2017 = load_nass_census_data(NASS_2017_FILE, 2017)
    if df_2017 is not None:
        processed_2017 = process_nass_census_data(df_2017, 2017)
        if processed_2017 is not None:
            processed_nass_data.append(processed_2017)
    
    # Process 2022 data
    df_2022 = load_nass_census_data(NASS_2022_FILE, 2022)
    if df_2022 is not None:
        processed_2022 = process_nass_census_data(df_2022, 2022)
        if processed_2022 is not None:
            processed_nass_data.append(processed_2022)
    
    return processed_nass_data

def main():
    """Main function to run the census data collection."""
    logger.info("Starting agricultural census data collection...")
    
    # Set up directories
    interim_dir = setup_directories()
    
    # Load deflator data
    deflator_df = load_deflator_data()
    if deflator_df is None:
        logger.error("Failed to load deflator data. Exiting.")
        return
    
    # Process ICPSR data (1992-2012)
    logger.info("Step 1: Processing ICPSR census data (1992-2012)...")
    icpsr_files, icpsr_missing = collect_census_files()
    
    # Process NASS data (2017, 2022)
    logger.info("Step 2: Processing NASS census data (2017, 2022)...")
    processed_nass_data = process_nass_data()
    
    # Combine all processed data
    all_processed_data = []
    collected_files = icpsr_files.copy()
    missing_files = icpsr_missing.copy()
    
    # Add NASS data to the collection
    if processed_nass_data:
        for nass_df in processed_nass_data:
            year = nass_df['year'].iloc[0]
            
            # Save individual year file
            year_file = interim_dir / str(year) / f"census_{year}_filtered.tsv"
            nass_df.to_csv(year_file, sep='\t', index=False)
            
            # Add to processed data list
            all_processed_data.append(nass_df)
            
            # Add to collected files summary
            collected_files.append({
                'year': year,
                'folder': 'NASS',
                'source': f'NASS_{year}',
                'destination': str(year_file),
                'rows': len(nass_df),
                'columns': len(nass_df.columns)
            })
    
    # Create merged dataset from all data
    if all_processed_data:
        logger.info("Step 3: Creating merged dataset...")
        
        # Load ICPSR data that was already processed
        icpsr_data = []
        for year in [1992, 1997, 2002, 2007, 2012]:
            year_file = interim_dir / str(year) / f"census_{year}_filtered.tsv"
            if year_file.exists():
                df = pd.read_csv(year_file, sep='\t', low_memory=False)
                icpsr_data.append(df)
        
        # Combine all data
        all_data = icpsr_data + all_processed_data
        merged_df = pd.concat(all_data, ignore_index=True)
        
        # Apply deflation
        logger.info("Step 4: Applying deflation...")
        merged_df_deflated = deflate_columns(merged_df, deflator_df, DEFLATABLE_COLS)
        
        # Create final datasets
        essential_columns = ['year', 'name', 'level', 'fips', 'statefip', 'counfip']
        real_columns = [f"{col}_real" for col in DEFLATABLE_COLS if f"{col}_real" in merged_df_deflated.columns]
        other_columns = [col for col in merged_df_deflated.columns if col not in essential_columns and not col.endswith('_real') and col not in DEFLATABLE_COLS]
        
        # Final dataset with deflated values
        final_columns = essential_columns + other_columns + real_columns
        available_final_columns = [col for col in final_columns if col in merged_df_deflated.columns]
        final_df = merged_df_deflated[available_final_columns].copy()
        
        # Full dataset without deflator columns
        full_columns = [col for col in merged_df_deflated.columns if col != 'price_deflator']
        full_df = merged_df_deflated[full_columns].copy()
        
        # Save final datasets
        final_file = interim_dir / "census_merged_1992_2022_deflated.tsv"
        final_df.to_csv(final_file, sep='\t', index=False)
        
        full_file = interim_dir / "census_merged_1992_2022_full.tsv"
        full_df.to_csv(full_file, sep='\t', index=False)
        
        logger.info(f"✓ Created deflated merged dataset: {final_file} ({len(final_df)} rows, {len(final_df.columns)} cols)")
        logger.info(f"✓ Created full dataset (nominal + real): {full_file} ({len(full_df)} rows, {len(full_df.columns)} cols)")
        
        # Add merged files to summary
        collected_files.extend([
            {
                'year': 'merged_deflated',
                'folder': 'all',
                'source': 'multiple',
                'destination': str(final_file),
                'rows': len(final_df),
                'columns': len(final_df.columns)
            },
            {
                'year': 'merged_full',
                'folder': 'all',
                'source': 'multiple',
                'destination': str(full_file),
                'rows': len(full_df),
                'columns': len(full_df.columns)
            }
        ])
    
    # Print summary
    print_summary(collected_files, missing_files)
    
    if collected_files:
        logger.info("Data collection completed successfully!")
    else:
        logger.warning("No files were collected. Please check the source paths.")

if __name__ == "__main__":
    main()
