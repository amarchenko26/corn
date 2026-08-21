// ============================================================================
// Descriptives on the income shocks (year-over-year change in the
// leave-one-county-out cell income, d_iv, in $10k units).
//
// Answers: which occupations do the shocks hit, and are they mostly
// positive or negative?
//
// Outputs (Overleaf):
//   tabs/labor_supply/shock_by_occupation.tex
//   figs/labor_supply/shock_distribution.png
//   figs/labor_supply/shock_density_by_occupation.png
// ============================================================================

clear all

global data     "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data"
global overleaf "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/Apps/Overleaf/nutrition"

use "$data/final/labor_supply_reg_data.dta", clear

// ============================================================================
// Occupation bins — same grouping as the IV cells (build/iv/build_iv.py):
// male head's occupation, female as fallback (this is the cell the HH shock
// is computed from)
// ============================================================================

gen occ_src = male_head_occupation
replace occ_src = female_head_occupation if missing(occ_src) | occ_src == 0

gen byte occ_bin = .
replace occ_bin = 1 if inrange(occ_src, 1, 4)      // Prof/Tech, Manager, Sales, Clerical
replace occ_bin = 2 if inrange(occ_src, 5, 7)      // Craftsman, Operative, Laborer
replace occ_bin = 3 if inlist(occ_src, 8, 9, 11)   // Service, Farmer, Student
replace occ_bin = 4 if inlist(occ_src, 10, 12)     // Not employed for pay
label define occ_bin_lbl 1 "White collar" 2 "Blue collar" 3 "Service/other" 4 "Not employed"
label values occ_bin occ_bin_lbl
label var occ_bin "Occupation bin (male head, female fallback)"

gen byte neg_shock = (d_iv < 0) if !missing(d_iv)

// ============================================================================
// Table: shocks by occupation bin
// ============================================================================

quietly count if !missing(d_iv)
local N_all = r(N)

matrix S = J(5, 5, .)
local r = 1
forvalues g = 1/4 {
	quietly summarize d_iv if occ_bin == `g'
	matrix S[`r',1] = r(N)
	matrix S[`r',2] = 100 * r(N) / `N_all'
	matrix S[`r',3] = r(mean)
	matrix S[`r',4] = r(sd)
	quietly summarize neg_shock if occ_bin == `g'
	matrix S[`r',5] = 100 * r(mean)
	local ++r
}
quietly summarize d_iv
matrix S[5,1] = r(N)
matrix S[5,2] = 100
matrix S[5,3] = r(mean)
matrix S[5,4] = r(sd)
quietly summarize neg_shock
matrix S[5,5] = 100 * r(mean)

// (shares are in percent; say so in the hand-written table note — a literal %
// in a matrix column name passes through to LaTeX unescaped and breaks the row)
matrix rownames S = "White collar" "Blue collar" "Service/other" "Not employed" "Total"
matrix colnames S = "N" "Share" "Mean" "SD" "Share neg."

esttab matrix(S, fmt(%12.0fc 1 3 3 1)) using "$overleaf/tabs/labor_supply/shock_by_occupation.tex", ///
	replace booktabs nomtitles nonotes

esttab matrix(S, fmt(%12.0fc 1 3 3 1))

// ============================================================================
// Figure: distribution of the shock (pooled)
// ============================================================================

quietly summarize neg_shock
local pctneg : display %4.1f 100 * r(mean)

histogram d_iv if inrange(d_iv, -1.5, 1.5), percent width(0.05) ///
	xline(0, lcolor(black) lwidth(medthick)) ///
	xtitle("Income shock ($10k)", size(medlarge)) ///
	ytitle("Percent of HH-years", size(medlarge)) ///
	xlabel(-1.5(0.5)1.5, labsize(medlarge)) ylabel(, labsize(medlarge)) ///
	note("`pctneg'% of shocks are negative. Display truncated at ±$15k.", size(medium))

graph export "$overleaf/figs/labor_supply/shock_distribution.png", replace width(2400)

// ============================================================================
// Figure: shock density by occupation bin
// ============================================================================

twoway (kdensity d_iv if occ_bin == 1 & inrange(d_iv, -1.5, 1.5), lwidth(thick)) ///
       (kdensity d_iv if occ_bin == 2 & inrange(d_iv, -1.5, 1.5), lwidth(thick)) ///
       (kdensity d_iv if occ_bin == 3 & inrange(d_iv, -1.5, 1.5), lwidth(thick)) ///
       (kdensity d_iv if occ_bin == 4 & inrange(d_iv, -1.5, 1.5), lwidth(thick) lpattern(dash)), ///
	xline(0, lcolor(gray)) ///
	xtitle("Income shock ($10k)", size(medlarge)) ytitle("Density", size(medlarge)) ///
	legend(order(1 "White collar" 2 "Blue collar" 3 "Service/other" 4 "Not employed") ///
	       rows(1) position(6) size(medlarge)) ///
	xlabel(-1.5(0.5)1.5, labsize(medlarge)) ylabel(, labsize(medlarge))

graph export "$overleaf/figs/labor_supply/shock_density_by_occupation.png", replace width(2400)
