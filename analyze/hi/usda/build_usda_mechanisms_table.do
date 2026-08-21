// ============================================================================
// build_usda_mechanisms_table.do -- USDA twin of tabs/expenditure.tex (the
// Mechanisms slide table). Mirrors the diet/spend loops in build_hi.do exactly:
// forward-diff IV, non-movers, HH/year/kids/age/composition FE, county-clustered.
//
// Column mapping vs the Syndigo original:
//   Total spend, Produce share  -- classification-free (Nielsen), re-run as-is
//   High sugar                  -- reclassified with USDA labels
//                                  (expenditure_hh_year_usda.dta, built by
//                                   build_expenditure_panel.py usda)
//   Calories, Sugar density     -- total_cals_usda, sugar_per_1000cal_usda
//
// Output: tabs/expenditure_usda.tex
// ============================================================================
clear all

global TABS "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/Apps/Overleaf/nutrition/tabs"
global PD   "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data/interim/panel_dataset"

// USDA-classified high-sugar spend, keyed to match final_reg_data's renames
use household_code panel_year spend_high_sugar using "$PD/expenditure_hh_year_usda.dta", replace
rename household_code hhid
rename panel_year year
rename spend_high_sugar spend_high_sugar_usda
tempfile usda_spend
save `usda_spend'

use "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data/final/final_reg_data.dta", replace
merge 1:1 hhid year using `usda_spend', keep(master match) nogen
xtset hhid year

local vars spend_total spend_high_sugar_usda spend_share_produce total_cals_usda sugar_per_1000cal_usda
foreach var of local vars {
	cap drop f_`var'
	gen f_`var' = F.`var' - `var'
}

eststo clear
foreach var of local vars {
	quietly eststo f_`var': ivreghdfe f_`var' (D.real_income=D.iv_income_fips) ///
		[pw = projection_factor] if movers_f == 0, ///
		absorb(year hhid kids avg_age_hh_head hh_comp) cluster(fips)
	quietly summarize f_`var' if e(sample)
	estadd scalar mean_y = r(mean): f_`var'
}

esttab f_spend_total f_spend_high_sugar_usda f_spend_share_produce f_total_cals_usda f_sugar_per_1000cal_usda ///
    using "$TABS/expenditure_usda.tex", replace ///
    keep(D.real_income) varlabels(D1.real_income "\(m_t\)") ///
    b(3) se(3) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
	mlabels("Total" "High sugar" "Produce share" "Calories" "Sugar density") ///
    mgroups("Expenditure (dollars per year)" "Nutrition Components", pattern(1 0 0 1 0) ///
        prefix(\multicolumn{@span}{c}{) suffix(}) ///
        span erepeat(\cmidrule(lr){@span})) ///
    collabels(none) ///
    booktabs ///
    stats(mean_y N, fmt(%9.0fc %9.0fc) labels("Mean outcome" "N")) ///
    nonotes

di "build_usda_mechanisms_table.do complete"
