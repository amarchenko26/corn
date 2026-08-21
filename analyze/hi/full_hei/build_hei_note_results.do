// ============================================================================
// build_hei_note_results.do -- regression numbers for notes/hei_simple_vs_full.tex:
// the main forward-difference income IV and its pre-trend placebo, run three
// ways: simple index (Syndigo), simple index (USDA), full HEI (USDA).
// All outcomes z-scored on the estimation sample so coefficients are
// comparable (SD per $10k). Spec identical to m7/m8 in build_hi.do.
// Prints a console esttab; numbers are transcribed into the note's tabular.
// ============================================================================
clear all
use "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data/final/final_reg_data.dta", replace
xtset hhid year
keep if movers_f == 0

local outcomes hi hi_usda hei_usda
foreach v of local outcomes {
	qui sum `v' [aw = projection_factor]
	gen z_`v'  = (`v' - r(mean)) / r(sd)
	gen fz_`v' = F.z_`v' - z_`v'
	gen dz_`v' = D.z_`v'
}

eststo clear
foreach v of local outcomes {
	eststo fwd_`v': ivreghdfe fz_`v' (D.real_income = D.iv_income_fips) ///
		[pw = projection_factor], ///
		absorb(year hhid kids avg_age_hh_head hh_comp) cluster(fips)
	eststo pre_`v': ivreghdfe dz_`v' (f_inc = f_iv) ///
		[pw = projection_factor], ///
		absorb(year hhid kids avg_age_hh_head hh_comp) cluster(fips)
}

esttab fwd_hi fwd_hi_usda fwd_hei_usda pre_hi pre_hi_usda pre_hei_usda, ///
	keep(D.real_income f_inc) b(4) se(4) ///
	star(* 0.10 ** 0.05 *** 0.01) ///
	mtitles("Fwd simple-Syn" "Fwd simple-USDA" "Fwd HEI" ///
	        "Pre simple-Syn" "Pre simple-USDA" "Pre HEI") ///
	stats(N, fmt(%9.0fc) labels("N"))

di "build_hei_note_results.do complete"
