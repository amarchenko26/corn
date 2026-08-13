"""Build USDA Branded Food -> per-100g wide nutrient table keyed by canonical UPC.
Mirrors syndigo_wide.parquet so it can be swapped into build_hi_panel's HI formula.

USDA food_nutrient.amount is already per-100g. Units: energy kcal; fat/satfat/fiber/sugar in G;
sodium & cholesterol in MG -> convert to G to match Syndigo/Allcott convention.
"""
import pandas as pd, numpy as np, os, time

USDA = '/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data/raw/usda/Branded Food/FoodData_Central_branded_food_csv_2024-04-18'
OUT  = '/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data/interim/usda_nielsen_merged/usda_wide.parquet'

# nutrient_id -> (colname, unit)  [USDA nutrient.csv ids]
NUT = {
    '1008': ('cal_per_100g',    'kcal'),
    '1258': ('satfat_per_100g', 'g'),
    '1253': ('chol_per_100g',   'mg'),   # -> g
    '1093': ('sodium_per_100g', 'mg'),   # -> g
    '1079': ('fiber_1079',      'g'),
    '2033': ('fiber_2033',      'g'),    # AOAC fallback
    '2000': ('sugar_2000',      'g'),
    '1063': ('sugar_1063',      'g'),    # fallback
    '1235': ('addsugar_per_100g','g'),   # bonus (not in Syndigo)
    '1004': ('totfat_per_100g', 'g'),
}
KEEP_IDS = set(NUT)

# ---------- 1. food_nutrient.csv (1.4GB) -> filter to HI nutrients, pivot wide ----------
t0 = time.time()
print("Parsing food_nutrient.csv in chunks...")
parts = []
rdr = pd.read_csv(os.path.join(USDA,'food_nutrient.csv'),
                  usecols=['fdc_id','nutrient_id','amount'],
                  dtype={'fdc_id':str,'nutrient_id':str,'amount':float},
                  chunksize=3_000_000)
for i, ch in enumerate(rdr):
    ch = ch[ch['nutrient_id'].isin(KEEP_IDS)]
    parts.append(ch)
    print(f"  chunk {i}: kept {len(ch):,} rows  ({time.time()-t0:.0f}s)")
fn = pd.concat(parts, ignore_index=True)
print(f"  total kept: {len(fn):,} nutrient rows for {fn['fdc_id'].nunique():,} fdc_ids")

wide = fn.pivot_table(index='fdc_id', columns='nutrient_id', values='amount', aggfunc='first')
wide = wide.rename(columns={k: v[0] for k, v in NUT.items()}).reset_index()

# coalesce fiber / sugar
wide['fiber_per_100g'] = wide.get('fiber_1079')
if 'fiber_2033' in wide: wide['fiber_per_100g'] = wide['fiber_per_100g'].fillna(wide['fiber_2033'])
wide['sugar_per_100g'] = wide.get('sugar_2000')
if 'sugar_1063' in wide: wide['sugar_per_100g'] = wide['sugar_per_100g'].fillna(wide['sugar_1063'])

# mg -> g
for c in ['chol_per_100g','sodium_per_100g']:
    wide[c] = wide[c] / 1000.0

# ---------- 2. branded_food.csv -> UPC + serving + category + dates ----------
print("\nLoading branded_food.csv (subset of cols)...")
bf = pd.read_csv(os.path.join(USDA,'branded_food.csv'),
                 usecols=['fdc_id','gtin_upc','serving_size','serving_size_unit',
                          'branded_food_category','available_date','modified_date'],
                 dtype={'fdc_id':str,'gtin_upc':str,'serving_size_unit':str,
                        'branded_food_category':str,'available_date':str,'modified_date':str},
                 low_memory=False)
bf['serving_size'] = pd.to_numeric(bf['serving_size'], errors='coerce')

# canonical UPC key: DROP CHECK DIGIT (Syndigo-style) so it matches Nielsen '0'+upc12.
# Nielsen stores upc as '0' + 11-digit-UPC-A-core (check digit removed); Syndigo does
# gtin.zfill(14)[:-1]. Mirror that exactly.
g = bf['gtin_upc'].astype(str).str.strip()
valid = g.str.fullmatch(r'\d+')
bf = bf[valid].copy()
bf['upc13'] = bf['gtin_upc'].str.strip().str.zfill(14).str[:-1]   # 13-digit, check dropped
bf['upc12'] = bf['gtin_upc'].str.strip().str.zfill(14).str[-12:]  # kept for reference only

# ---------- 3. merge nutrients onto products ----------
df = bf.merge(wide, on='fdc_id', how='left')

# ---------- 4. dedup to one row per upc12 (multiple fdc_ids share a UPC) ----------
NUTCOLS = ['cal_per_100g','satfat_per_100g','chol_per_100g','sodium_per_100g',
           'fiber_per_100g','sugar_per_100g','addsugar_per_100g','totfat_per_100g']
df['n_complete'] = df[NUTCOLS].notna().sum(axis=1)
df['recency'] = pd.to_datetime(df['modified_date'], errors='coerce').fillna(
                pd.to_datetime(df['available_date'], errors='coerce'))
# prefer: has calories, then most complete, then most recent
df['has_cal'] = df['cal_per_100g'].notna().astype(int)
df = df.sort_values(['upc13','has_cal','n_complete','recency'],
                    ascending=[True, False, False, False])
usda = df.drop_duplicates('upc13', keep='first').copy()

keep = ['upc13','upc12','gtin_upc','serving_size','serving_size_unit','branded_food_category'] + NUTCOLS + ['fiber_per_100g']
keep = list(dict.fromkeys([c for c in keep if c in usda.columns]))
usda = usda[keep]

# cap impossible values (unit misclassification), mirror merge_nielsen_syn
usda.loc[usda['sodium_per_100g'] > 5, 'sodium_per_100g'] = np.nan
usda.loc[usda['chol_per_100g']   > 2, 'chol_per_100g']   = np.nan

usda.to_parquet(OUT, index=False)
print(f"\nSaved {OUT}")
print(f"USDA unique UPCs: {len(usda):,}")
for c in NUTCOLS:
    print(f"  {c}: non-null {usda[c].notna().sum():,} ({usda[c].notna().mean():.0%})")
print("\nUPC length distribution of source gtin (pre-canonical):")
print(bf['gtin_upc'].str.len().value_counts().sort_index().to_string())
