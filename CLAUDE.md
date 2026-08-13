# nutrition_code — project guide

Paper: **"Why Don't Americans Eat Better? Income, Innovation, and Nutrition"** (Marchenko, JMP).
Two parts: (1) consumer/PE — causal effect of income on nutrition (leave-one-out income IV); (2) firm/GE
— product innovation skews toward unhealthy food. Data: Nielsen Consumer Panel (HMS) + RMS scanner,
Syndigo labels, USDA FoodData Central (Branded), ACS.

## Repo layout (verb-first; reorganized 2026-08-13)

Filenames are **verb-first**, labelled by dataset (`clean_syndigo`, `merge_nielsen_syndigo`,
`build_hi_panel`, `analyze_variety_price_index`). One job per script. `1_`/`2_` prefix ordered steps.
**Data lives in Dropbox, never the repo; figures/tables write to the Overleaf project.**

```
clean/     raw → tidy, per source
  nielsen/   clean_nielsen · clean_panelist · clean_ailments · validate_ailments · create_sample
  syndigo/   clean_syndigo · merge_nielsen_syndigo         → interim/syndigo_nielsen_merged/syndigo_wide.parquet
  usda/      build_usda_wide                               → interim/usda_nielsen_merged/usda_wide.parquet
build/     analytic panels & variables
  hi/          build_hi_panel · build_hi_usda_panel · build_claude_hi · add_sodium_to_panel · export_hi_usda_dta
  iv/          build_iv · build_county_income_shock · build_bartik_bls_iv · build_bartik_bls_module_iv · build_jaravel_ssiv
  variety/     build_product_variety · build_module_healthiness · build_module_income_elasticity · build_upc_spending · build_price_index (+ run_*.sh)
  innovation/  build_innovation_reg_data · build_upc_first_year_county (+ run_*.sh)
  expenditure/ build_expenditure_panel · build_trips_panel
  prep_time/   build_prep_time_index · build_prep_time_panel
  monthly_cycle/ build_monthly_cycle_panel
analyze/   regressions & figures
  hi/          build_hi.do (assembly + main IV regs) · verify_hi_usda.do · figure_hi_over_time · figure_predicted_vs_actual_hi · replicate_figure1
  variety/     analyze_variety_healthiness · analyze_variety_price_index
  innovation/  analyze_innovation_inequality · innovation.do
  monthly_cycle/ build_monthly_cycle_regs.do
utils/     food_filters (shared department/group/module drop lists)
z_archive/ retired: corn/ (separate farm-bill project), explore_coverage.py, fracking.do
food_deserts_replication/, jaravel_replication/   standalone external replications (left as-is)
```

Cross-folder Python imports use a `sys.path` bootstrap (only in `build/variety/build_module_healthiness.py`
and `build_product_variety.py`, which reach `utils/` and `clean/syndigo/`). `.sh` runners are Oscar/SLURM
cluster jobs hardcoding `/users/amarche4/scratch/` — repo location is irrelevant to them.

## Data & output locations

- **Nielsen data root:** `/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data`
  — `raw/` (consumer `.tgz`, RMS `products.tsv`, `syndigo/`, `usda/`), `interim/` (built panels/caches), `final/`.
- Panelist tsvs are extracted from inside `Consumer_Panel_Data_{year}.tgz` (tar member
  `nielsen_extracts/HMS/…`) — this is an archive path, **not** a repo folder.
- **Overleaf paper:** `/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/Apps/Overleaf/nutrition`
  (`figs/`, `tabs/`, `notes/`). Scripts write outputs straight here.

## Health Index (main outcome)

Allcott et al. (2019): fixed positive score for fruit/veg modules; for all else,
`fiber/29.5 − sugar/32.8 − satfat/17.2 − sodium/2.3 − chol/0.3` per 100 g → per-1,000 kcal →
calorie-weighted to household-year → standardized. Produce/whole-grain flags come from Nielsen
modules (source-independent). Built by `build/hi/build_hi_panel.py` →
`interim/panel_dataset/panel_hh_year.parquet` (column `hi`). USDA-based analog `hi_usda` via
`build_hi_usda_panel.py` (validated: Syndigo-mode reproduces `hi` at corr 1.000). Main IV regressions in
`analyze/hi/build_hi.do` — forward-difference 2SLS, leave-one-out county income instrument, non-movers,
HH/year/kids/age/composition FE, county-clustered SE. UPC harmonization: Nielsen `'0'+zfill(upc,12)`;
external GTINs harmonize by dropping the check digit (`gtin.zfill(14)[:-1]`).

## Labor-supply subsystem (built in `clean/nielsen/clean_panelist.py`, used in `analyze/hi/build_hi.do`)

**Nielsen head/member caveats (shape everything):**
- No single "household head." Two fixed slots `male_head_*`/`female_head_*`; whether a HH reports **1 or 2
  heads is self-reported** at signup (not forced by marital status) — ~37% of HH-years report one head.
- Non-heads appear as `Member_1..7`. `n_members = household_size − n_heads` holds ~always (no adult dropped).
  `Member_N_Relationship_Sex`: 1 Son, 2 Daughter, 3/4 other male/female relative, 5/6 male/female unrelated —
  **there is NO spouse/partner code**.
- **Head employment is an hours bin** (0 none, 1 <30h, 2 30–34h, 3 35+h, 9 not employed);
  **member employment is binary** (1 employed / blank). So a dual-earner couple is measured differently by
  self-reported head count → heads-only measures **undercount second earners in one-head HHs** (a bias,
  likely correlated with gender norms — not just missing data).

**Variables added to `panelists_all_years.parquet`/`.dta`:**
`male_head_status`/`female_head_status` (FT=code3 / PT=codes1,2 / NE=code9); `male/female_head_employed`
(1/0, missing if no such head); `n_heads`; `n_head_earners`; `hh_total_workhours` (summed head hours
{1→20,2→32,3→40,9→0}); `has_recovered_partner`, `recovered_partner_sex`, `n_recovered_partner_earners`;
`n_earners_total` (= head earners + recovered-partner earners — the extensive-margin count that is
**consistent across the 1-vs-2-head split**). Pre-existing (unchanged): `hh_avg_workhours`,
`hh_avg_workhours_if_employed`, `hh_employed`.

**Recovered partner** (proxy for a working spouse a one-head HH declined to mark as head): flagged only in
single-head HHs, a member who is opposite-sex to the head, adult (≥18), non-child (rel. codes 3/4/5/6), and
spouse-aged (within ±15y of head's binned-age midpoint). Kept as a separate flagged measure so it never
contaminates head-only analysis.

**`panelist_heads_long.parquet`:** one row per `household_code × panel_year × role`
(role ∈ male_head/female_head/partner) with `status`, `employed`, `margin`, `status_lag`, `transition`
(e.g. `FT->PT`). Transitions computed **for heads only** (head slots stable across years; member slots are
not). Full-panel counts (2004–2024): `n_heads` 1→445,531 · 2→757,915 HH-yrs; recovered partners 21,376;
long panel 1,982,737 rows.

**TODO — head-specific instruments:** `build/iv/build_iv.py` currently assigns one HH income shock via the
head's occupation (male-preferred). To separate own vs cross-spouse labor response, build
`iv_income_male`/`iv_income_female` (each from its own head's education×occupation cell) and regress each
head's employment transition on both in `panelist_heads_long`.

## Conventions
Verb-first dataset-labelled filenames; stage folders (clean/build/analyze); centralize paths; data out of
the repo. Overleaf notes: never compile locally (she compiles); concise write-ups (state a result once —
short table title, footnote for spec details only, ≤3 sentences of interpretation).
