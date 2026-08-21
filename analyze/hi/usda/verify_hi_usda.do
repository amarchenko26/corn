*==============================================================================
* verify_hi_usda.do  --  self-contained check that the main IV result holds when
* the Health Index is built from USDA instead of Syndigo.
* Mirrors the data prep in build_hi.do (m7 forward-diff, m8 pre-trend, non-movers).
* Uses ivreghdfe throughout (no Julia) so it runs in batch mode.
*==============================================================================
clear all
set more off
local NL "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data"

pq use using "`NL'/interim/panel_dataset/panel_hh_year.parquet", clear

merge 1:1 household_code panel_year using "`NL'/interim/panelists/panelists_all_years.dta", ///
    keepusing(age_and_presence_of_children household_composition fips_county_code fips_state_code) ///
    keep(master match) nogen
merge 1:1 household_code panel_year using "`NL'/interim/panel_dataset/iv_income.dta", ///
    keepusing(iv_income_fips) keep(master match) nogen
merge 1:1 household_code panel_year using "`NL'/interim/panel_dataset/hi_usda_panel.dta", ///
    keepusing(hi_usda) keep(master match) nogen

rename *, lower
tostring fips_state_code,  replace format(%02.0f)
tostring fips_county_code, replace format(%03.0f)
gen fips = fips_state_code + fips_county_code
egen long fips_n = group(fips)                 // numeric cluster id (identical groups)

ren age_and_presence_of_children kids
ren household_composition        hh_comp
ren household_code               hhid
ren panel_year                   year

winsor2 hi,      replace cuts(1 99)
winsor2 hi_usda, replace cuts(1 99)
replace real_income = real_income / 10

* non-FIPS-movers (matches m7/m8 sample)
bysort hhid fips (year): gen byte uniq_fips = (_n == 1)
bysort hhid: egen n_unique_fips = total(uniq_fips)
gen byte movers_f = (n_unique_fips > 1)

xtset hhid year
gen f_hi      = F.hi      - hi
gen f_hi_usda = F.hi_usda - hi_usda
gen f_inc     = F.real_income     - real_income
gen f_iv      = F.iv_income_fips  - iv_income_fips

keep if movers_f == 0

di "================= FORWARD DIFF (main IV): Syndigo vs USDA ================="
eststo m7:      ivreghdfe f_hi      (D.real_income=D.iv_income_fips) [pw = projection_factor], ///
    absorb(year hhid kids avg_age_hh_head hh_comp) cluster(fips_n)
eststo m7_usda: ivreghdfe f_hi_usda (D.real_income=D.iv_income_fips) [pw = projection_factor], ///
    absorb(year hhid kids avg_age_hh_head hh_comp) cluster(fips_n)

di "================= PRE-TREND (placebo): Syndigo vs USDA ==================="
eststo m8:      ivreghdfe D.hi      (f_inc = f_iv) [pw = projection_factor], ///
    absorb(year hhid kids avg_age_hh_head hh_comp) cluster(fips_n)
eststo m8_usda: ivreghdfe D.hi_usda (f_inc = f_iv) [pw = projection_factor], ///
    absorb(year hhid kids avg_age_hh_head hh_comp) cluster(fips_n)

esttab m7 m7_usda m8 m8_usda, ///
    keep(D.real_income f_inc) b(4) se(4) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("FwdDiff Syndigo" "FwdDiff USDA" "Pretrend Syndigo" "Pretrend USDA") ///
    stats(N, fmt(%9.0fc) labels("N"))

* correlation of the two indices on the estimation sample
corr hi hi_usda
