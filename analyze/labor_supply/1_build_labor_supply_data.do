// ============================================================================
// Assemble the labor-supply regression panel.
//
// Loads final_reg_data (assembled by analyze/hi/syndigo/build_hi.do), adds the
// raw head hour-bin codes + female head occupation from the panelist file and
// the head-specific income IVs (build/iv/build_iv_by_head.py), constructs
// per-head labor supply outcomes and shock variables, and saves
// final/labor_supply_reg_data.dta.
//
// Nielsen labor supply coding (see clean/nielsen/clean_panelist.py):
//   Head employment is an HOURS BIN: 1 = <30h, 2 = 30-34h, 3 = 35+h,
//   9 = not employed, 0 = no such head. Hours points: 1->20, 2->32, 3->40, 9->0.
//   Member (non-head) employment is BINARY (1 = employed / blank).
// ============================================================================

clear all

global data     "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data"

use "$data/final/final_reg_data.dta", clear

// ============================================================================
// Merge raw head employment bins, female head occupation, marital status
// (final_reg_data keeps only the derived FT/PT/NE statuses)
// ============================================================================

ren hhid household_code
ren year panel_year

merge 1:1 household_code panel_year using "$data/interim/panelists/panelists_all_years.dta", ///
	keepusing(male_head_employment female_head_employment female_head_occupation marital_status) ///
	keep(master match)
drop _merge

// Head-specific leave-one-county-out income IVs (own educ x occ cell per head)
merge 1:1 household_code panel_year using "$data/interim/panel_dataset/iv_income_by_head.dta", ///
	keepusing(iv_income_male_fips iv_income_female_fips ///
	          iv_cell_n_lo_male_fips iv_cell_n_lo_female_fips) ///
	keep(master match)
drop _merge

ren household_code hhid
ren panel_year year

xtset hhid year

// ============================================================================
// Per-head labor supply outcomes
// ============================================================================

// Weekly hours from the Nielsen hour-bin codes (missing if no such head)
foreach h in male female {
	cap drop `h'_head_hours
	gen `h'_head_hours = .
	replace `h'_head_hours = 20 if `h'_head_employment == 1
	replace `h'_head_hours = 32 if `h'_head_employment == 2
	replace `h'_head_hours = 40 if `h'_head_employment == 3
	replace `h'_head_hours = 0  if `h'_head_employment == 9
	label var `h'_head_hours "`h' head weekly work hours (0 if not employed)"
}

// FT/PT/NE indicators per head — missing (not 0) when the head doesn't exist
// (moved here from analyze/hi/syndigo/build_hi.do)
foreach h in male female {
	cap drop `h'_ft `h'_pt `h'_ne
	gen byte `h'_ft = (`h'_head_status == "FT") if `h'_head_status != ""
	gen byte `h'_pt = (`h'_head_status == "PT") if `h'_head_status != ""
	gen byte `h'_ne = (`h'_head_status == "NE") if `h'_head_status != ""
	label var `h'_ft "`h' head works full-time (35+ hrs)"
	label var `h'_pt "`h' head works part-time (<35 hrs)"
	label var `h'_ne "`h' head not employed for pay"
}

// Labels for the extensive-margin / recovery vars (moved from build_hi.do)
label var n_head_earners             "Employed heads (0-2)"
label var n_earners_total            "Employed adults incl. recovered partner"
label var hh_total_workhours         "Summed head work hours (absent head = 0)"
cap label define yesno 0 "No" 1 "Yes"
label values has_recovered_partner yesno
label var has_recovered_partner      "Single-head HH w/ opposite-sex spouse-aged earner"

// ============================================================================
// Forward differences (t+1 minus t) of labor supply outcomes + nutrition
// ============================================================================

foreach v in hh_avg_workhours hh_employed hh_total_workhours ///
             male_head_employed female_head_employed ///
             male_head_hours female_head_hours male_ft female_ft hi {
	cap drop f_`v'
	gen f_`v' = F.`v' - `v'
}
cap drop f_hh_avg_workhours_emp
gen f_hh_avg_workhours_emp = F.hh_avg_workhours_if_employed - hh_avg_workhours_if_employed

label var f_male_head_hours   "Change in male head hours (t+1 - t)"
label var f_female_head_hours "Change in female head hours (t+1 - t)"

// ============================================================================
// Shocks: year-over-year change in the leave-one-county-out cell income
// Raw IVs are in $1,000s; divide by 10 so shocks are in $10k units, matching
// real_income in the main regressions.
// ============================================================================

cap drop d_iv d_iv_male d_iv_female
gen d_iv        = D.iv_income_fips        / 10
gen d_iv_male   = D.iv_income_male_fips   / 10
gen d_iv_female = D.iv_income_female_fips / 10
label var d_iv        "HH shock (male-preferred cell, $10k)"
label var d_iv_male   "Male head shock ($10k)"
label var d_iv_female "Female head shock ($10k)"

// Own-occupation stability: the head's occupation code is unchanged from t-1,
// so their shock reflects movement in the cell's income, not the head
// switching cells (e.g. into the not-employed cell after losing a job)
foreach h in male female {
	cap drop `h'_occ_stable
	gen byte `h'_occ_stable = (`h'_head_occupation == L.`h'_head_occupation) ///
		if !missing(`h'_head_occupation) & !missing(L.`h'_head_occupation) ///
		 & `h'_head_occupation != 0
	label var `h'_occ_stable "`h' head occupation unchanged from t-1"
}

// Sign combinations of the two head shocks (couples with both shocks defined)
cap drop shock_combo opp_sign
gen byte shock_combo = .
replace shock_combo = 1 if d_iv_male > 0 & d_iv_female > 0 & !missing(d_iv_male, d_iv_female)
replace shock_combo = 2 if d_iv_male < 0 & d_iv_female < 0 & !missing(d_iv_male, d_iv_female)
replace shock_combo = 3 if d_iv_male > 0 & d_iv_female <= 0 & !missing(d_iv_male, d_iv_female)
replace shock_combo = 4 if d_iv_male <= 0 & d_iv_female > 0 & !missing(d_iv_male, d_iv_female)
label define shock_combo_lbl 1 "Both positive" 2 "Both negative" ///
                             3 "Male +, female -" 4 "Male -, female +"
label values shock_combo shock_combo_lbl
label var shock_combo "Sign combination of head shocks"

gen byte opp_sign = inlist(shock_combo, 3, 4) if !missing(shock_combo)
label var opp_sign "Head shocks have opposite signs"

// ============================================================================
// Baseline income quartiles (for heterogeneity splits)
// ============================================================================

cap drop baseline_income inc_q
bysort hhid (year): gen baseline_income = real_income[1]
xtile inc_q = baseline_income [aw = projection_factor], nquantiles(4)
label var inc_q "Baseline income quartile"

// ============================================================================
// Save
// ============================================================================

save "$data/final/labor_supply_reg_data.dta", replace
