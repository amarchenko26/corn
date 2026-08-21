"""Build the interim tables behind the Syndigo-vs-USDA comparison note (full panel).

One pass over purchases_food (2004-2020), matching every purchase row to both
nutrition dictionaries. Replaces the ad-hoc (lost) scripts that built the note's
original figures on a 5,000-HH sample.

Outputs (BASE/interim/usda_comparison/):
  upc_universe.parquet     -- one row per UPC in the Nielsen purchase universe:
                              pooled real spend, n purchases, dept/module, fruit/veg flags,
                              match flags to each source (has-calories & complete-macro tiers),
                              per-UPC HI per 1000 kcal under each source, module claude_hi_norm
  coverage_by_year.parquet -- per panel_year: total/matched spend & rows by source-tier,
                              plus spend-weighted claude_hi sums for the non-produce
                              selectivity panel (all / USDA-matched / USDA-unmatched / Syndigo-matched)
  hh_year_bothmatched.parquet -- HH-year HI under BOTH sources computed on the
                              both-matched purchase rows only (same rows, same grams,
                              same fruit/veg scoring; only nutrient values differ)

Downstream: 2_figure_coverage_bars.py, 3_figure_nutrient_agreement.py,
            4_figure_hi_comparison.py, 5_figure_coverage_over_time.py
"""
import pandas as pd
import numpy as np
from pathlib import Path
import gc, time

def log(msg):
    print(msg, flush=True)

# ============================================================
# SETTINGS (mirrors build/hi/build_hi_panel.py)
# ============================================================
BASE      = Path('/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data')
PURCHASES = BASE / 'interim' / 'purchases_food'
SYNDIGO   = BASE / 'interim' / 'syndigo_nielsen_merged' / 'syndigo_wide.parquet'
USDA      = BASE / 'interim' / 'usda_nielsen_merged' / 'usda_wide.parquet'
CLAUDEHI  = BASE / 'interim' / 'rms_variety' / 'claude_hi_scores.parquet'
OUT_DIR   = BASE / 'interim' / 'usda_comparison'
OUT_DIR.mkdir(parents=True, exist_ok=True)

YEARS           = range(2004, 2021)
MIN_ANNUAL_CALS = 50_000   # same HH-year calorie floor as build_hi_panel

UNIT_TO_GRAMS = {
    'OZ': 28.3495, 'LB': 453.592, 'FL OZ': 29.5735, 'QT': 946.353,
    'GAL': 3785.41, 'ML': 1.0, 'LT': 1000.0, 'KG': 1000.0, 'GM': 1.0, 'GR': 1.0,
}
FRUIT_GROUPS        = {'FRUIT - CANNED', 'FRUIT - DRIED', 'FRUIT'}
FRUIT_MODULES_FRESH = {4010, 4085, 4180, 4225, 4355, 4470}
VEG_GROUPS          = {'VEGETABLES - CANNED', 'VEGETABLES-FROZEN', 'VEGETABLES AND GRAINS - DRIED'}
VEG_MODULES_FRESH   = {4015, 4020, 4023, 4050, 4055, 4060, 4140, 4230, 4275, 4280, 4350, 4400, 4415, 4460, 4475}

PURCH_COLS = ['upc', 'household_code', 'quantity', 'total_price_paid_real_2013',
              'size1_amount', 'size1_units', 'department_descr', 'product_group',
              'product_module', 'product_module_code']

# ============================================================
# DICTIONARIES
# ============================================================
log("Loading nutrition dictionaries...")
syn = pd.read_parquet(SYNDIGO).rename(columns={'upc': 'upc_13'})
usda = pd.read_parquet(USDA).rename(columns={'upc13': 'upc_13'})

def add_flags(df, pre):
    """has-calories and complete-macro (cal+sugar+satfat+sodium) tiers."""
    df[f'{pre}_cal'] = df['cal_per_100g'].notna()
    df[f'{pre}_macro'] = (df['cal_per_100g'].notna() & df['sugar_per_100g'].notna()
                          & df['satfat_per_100g'].notna() & df['sodium_per_100g'].notna())
    return df

syn = add_flags(syn, 'syn')
usda = add_flags(usda, 'usda')

NUT = ['cal_per_100g', 'fiber_per_100g', 'sugar_per_100g',
       'satfat_per_100g', 'sodium_per_100g', 'chol_per_100g']
syn_m = syn[['upc_13', 'syn_cal', 'syn_macro'] + NUT].rename(columns={c: f's_{c}' for c in NUT})
usda_m = usda[['upc_13', 'usda_cal', 'usda_macro'] + NUT].rename(columns={c: f'u_{c}' for c in NUT})

chi = pd.read_parquet(CLAUDEHI)[['product_module_code', 'claude_hi_norm']]

def hi_per_1000cal(df, pre, is_fv, is_fruit, is_veg):
    """Allcott HI per 1000 kcal under source prefix `pre` ('s' or 'u')."""
    hi100 = np.where(
        is_fv,
        is_fruit.astype(float) * 100 / 320 + is_veg.astype(float) * 100 / 390,
        df[f'{pre}_fiber_per_100g'].fillna(0) / 29.5
        - df[f'{pre}_sugar_per_100g'].fillna(0) / 32.8
        - df[f'{pre}_satfat_per_100g'].fillna(0) / 17.2
        - df[f'{pre}_sodium_per_100g'].fillna(0) / 2.3
        - df[f'{pre}_chol_per_100g'].fillna(0) / 0.3,
    )
    return hi100 / df[f'{pre}_cal_per_100g'] * 1000

# ============================================================
# ONE PASS OVER PURCHASES
# ============================================================
upc_parts, cov_rows, bm_parts = [], [], []
t0 = time.time()

for year in YEARS:
    ppath = PURCHASES / f'panel_year={year}'
    if not ppath.exists():
        log(f"  {year}: no data, skipping")
        continue
    purch = pd.read_parquet(ppath, columns=PURCH_COLS)
    purch = purch[purch['department_descr'] != 'MAGNET DATA']
    purch['upc_13'] = '0' + purch['upc'].astype(str).str.zfill(12)

    purch['is_fruit'] = (
        purch['product_group'].isin(FRUIT_GROUPS)
        | purch['product_module_code'].isin(FRUIT_MODULES_FRESH)
        | purch['product_module'].str.contains('FROZEN FRUITS|FRUIT JUICE|FRUIT DRINK', case=False, na=False))
    purch['is_veg'] = (
        purch['product_group'].isin(VEG_GROUPS)
        | purch['product_module_code'].isin(VEG_MODULES_FRESH)
        | purch['product_module'].str.contains(
            'VEGETABLE.*FROZEN|TOMATO PASTE|TOMATO SAUCE|TOMATO PUREE|TOMATOES.*CANNED|TOMATOES.*STEWED|MUSHROOM',
            case=False, na=False))

    purch = purch.merge(syn_m, on='upc_13', how='left').merge(usda_m, on='upc_13', how='left')
    # cast back to bool: the left-merge upcasts to OBJECT dtype, on which `~`
    # silently does integer bitwise-NOT (~True=-2, truthy!) and corrupts masks
    for f in ['syn_cal', 'syn_macro', 'usda_cal', 'usda_macro']:
        purch[f] = purch[f].fillna(False).astype(bool)
    purch = purch.merge(chi, on='product_module_code', how='left')

    spend = purch['total_price_paid_real_2013']

    # ---- coverage-by-year row ------------------------------------------
    nonprod = ~(purch['is_fruit'] | purch['is_veg'])
    np_ok = nonprod & purch['claude_hi_norm'].notna()
    row = {'panel_year': year,
           'spend_total': spend.sum(), 'rows_total': len(purch)}
    for f in ['syn_cal', 'syn_macro', 'usda_cal', 'usda_macro']:
        row[f'spend_{f}'] = spend[purch[f]].sum()
        row[f'rows_{f}'] = int(purch[f].sum())
    for name, m in [('np_all', np_ok),
                    ('np_usda', np_ok & purch['usda_cal']),
                    ('np_usda_un', np_ok & ~purch['usda_cal']),
                    ('np_syn', np_ok & purch['syn_cal'])]:
        row[f'spend_{name}'] = spend[m].sum()
        row[f'hiwt_{name}'] = (spend[m] * purch.loc[m, 'claude_hi_norm']).sum()
    cov_rows.append(row)

    # ---- per-UPC aggregate ---------------------------------------------
    agg = purch.groupby('upc_13').agg(
        spend=('total_price_paid_real_2013', 'sum'),
        n_purch=('upc_13', 'size'),
        department_descr=('department_descr', 'first'),
        product_group=('product_group', 'first'),
        product_module=('product_module', 'first'),
        product_module_code=('product_module_code', 'first'),
        is_fruit=('is_fruit', 'first'),
        is_veg=('is_veg', 'first'),
    ).reset_index()
    upc_parts.append(agg)

    # ---- both-matched HH-year HI (same rows, same grams, same F/V) -----
    bm = purch[purch['syn_cal'] & purch['usda_cal']].copy()
    bm['g_conv'] = bm['size1_units'].map(UNIT_TO_GRAMS) * bm['size1_amount']
    is_fv = bm['is_fruit'] | bm['is_veg']
    for pre in ['s', 'u']:
        bm[f'{pre}_cals'] = bm['quantity'] * bm['g_conv'] * bm[f'{pre}_cal_per_100g'] / 100
        bm[f'{pre}_hi1000'] = hi_per_1000cal(bm, pre, is_fv, bm['is_fruit'], bm['is_veg'])
        bm[f'{pre}_wt_hi'] = bm[f'{pre}_hi1000'] * bm[f'{pre}_cals']
    bm = bm[bm['s_cals'].notna() & (bm['s_cals'] > 0) & bm['u_cals'].notna() & (bm['u_cals'] > 0)]
    bm_agg = bm.groupby('household_code').agg(
        s_cals=('s_cals', 'sum'), s_wt=('s_wt_hi', 'sum'),
        u_cals=('u_cals', 'sum'), u_wt=('u_wt_hi', 'sum')).reset_index()
    bm_agg['panel_year'] = year
    bm_parts.append(bm_agg)

    log(f"  {year}: {len(purch):,} rows, ${spend.sum()/1e9:.2f}B, "
        f"usda {row['spend_usda_cal']/row['spend_total']:.0%} / syn {row['spend_syn_cal']/row['spend_total']:.0%} spend-matched "
        f"({time.time()-t0:.0f}s)")
    del purch, agg, bm, bm_agg
    gc.collect()

# ============================================================
# COMBINE + SAVE
# ============================================================
log("Combining UPC universe...")
u = pd.concat(upc_parts, ignore_index=True)
u = u.groupby('upc_13').agg(
    spend=('spend', 'sum'), n_purch=('n_purch', 'sum'),
    department_descr=('department_descr', 'first'),
    product_group=('product_group', 'first'),
    product_module=('product_module', 'first'),
    product_module_code=('product_module_code', 'first'),
    is_fruit=('is_fruit', 'first'), is_veg=('is_veg', 'first'),
).reset_index()

u = u.merge(syn_m, on='upc_13', how='left').merge(usda_m, on='upc_13', how='left')
for f in ['syn_cal', 'syn_macro', 'usda_cal', 'usda_macro']:
    u[f] = u[f].fillna(False).astype(bool)
is_fv = u['is_fruit'] | u['is_veg']
u['hi1000_syn'] = hi_per_1000cal(u, 's', is_fv, u['is_fruit'], u['is_veg'])
u['hi1000_usda'] = hi_per_1000cal(u, 'u', is_fv, u['is_fruit'], u['is_veg'])
u = u.merge(chi, on='product_module_code', how='left')
u.drop(columns=[c for c in u.columns if c.startswith(('s_', 'u_'))], inplace=True)
u.to_parquet(OUT_DIR / 'upc_universe.parquet', index=False)
log(f"  upc_universe: {len(u):,} UPCs, ${u['spend'].sum()/1e9:.1f}B, {u['n_purch'].sum()/1e6:.1f}M purchases")

cov = pd.DataFrame(cov_rows)
cov.to_parquet(OUT_DIR / 'coverage_by_year.parquet', index=False)
log(f"  coverage_by_year: {len(cov)} years")

bm = pd.concat(bm_parts, ignore_index=True)
bm = bm[(bm['s_cals'] >= MIN_ANNUAL_CALS) & (bm['u_cals'] >= MIN_ANNUAL_CALS)]
bm['rHI_syn_bm'] = bm['s_wt'] / bm['s_cals']
bm['rHI_usda_bm'] = bm['u_wt'] / bm['u_cals']
bm = bm[['household_code', 'panel_year', 's_cals', 'u_cals', 'rHI_syn_bm', 'rHI_usda_bm']]
bm.to_parquet(OUT_DIR / 'hh_year_bothmatched.parquet', index=False)
log(f"  hh_year_bothmatched: {len(bm):,} HH-years")
log(f"Done in {time.time()-t0:.0f}s")
