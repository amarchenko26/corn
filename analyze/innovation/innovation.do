clear all 

gl data "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/nielsen_data/"

// ============================================================================
// Make data
// ============================================================================

// healthiness
use "$data/interim/rms_variety/variety_healthiness_module.dta", clear
ren product_module_code module_code
ren product_module_descr module_descr
ren product_group_code group_code
ren product_group_descr group_descr
tempfile module_nutrition
save `module_nutrition'

// jaravel demographic iv 
use "$data/interim/panel_dataset/jaravel_ssiv.dta", clear
ren product_module_code module_code
tempfile jaravel_iv
save `jaravel_iv'

// income elasticity from previous IV 
use "$data/interim/panel_dataset/module_income_elasticity.dta", clear
ren product_module_code module_code
tempfile elasticity
save `elasticity'

// BLS bartk 
use "$data/interim/panel_dataset/bartik_bls_module_iv.dta", clear
tempfile bls
save `bls'

// Load our regression data 
use "$data/interim/panel_dataset/innovation_reg_data.dta", clear

// Merge to healthiness 
merge m:1 module_code using `module_nutrition', ///
	keepusing(module_descr group_code group_descr claude_hi claude_hi_z hi_per_100g hi_per_100g_z sugar_per_100g sodium_per_100g)
	
merge m:1 module_code using `elasticity', keepusing(eta_iv eta_iv_raw) nogen

merge 1:1 module_code year using `bls', keepusing(iv_bartik_bls) nogen



// ============================================================================
// FIGS  
// ============================================================================

preserve 

collapse (mean) ssnp spending eta_iv hi_per_100g sugar_per_100g sodium_per_100g n_new_upcs n_upcs, by(module_code)

merge 1:1 module_code using `module_nutrition', keepusing(module_descr)

reg sugar_per_100g eta_iv [aw=spending], r
reg sodium_per_100g eta_iv [aw=spending], r
reg hi_per_100g eta_iv [aw=spending], r
reg ssnp eta_iv [aw=spending], r

restore 

// ============================================================================
// INCOME ELASTICITY -- do not collapse to module level  
// ============================================================================

cap drop hi_q
xtile hi_q = hi_per_100g, n(4)


reghdfe hi_per_100g eta_iv, cluster(module_code)

reghdfe hi_per_100g eta_iv, absorb(year) cluster(module_code)

reghdfe hi_per_100g eta_iv [aw=spending], absorb(year) cluster(module_code)

* Main result: does income elasticity of demand predict module-level innovation?
reg ssnp eta_iv [aw=sqrt(spending)], r

reg ssnp b4.hi_q [aw=sqrt(spending)], r


* Heterogeneity: is the elasticity-innovation link stronger in healthy modules?
reghdfe ssnp c.eta_iv##ib4.hi_q [aw=spending], absorb(year) cluster(module_code)





// ============================================================================
// INCOME ELASTICITY -- collapsed to module level  
// ============================================================================

collapse (mean) ssnp spending eta_iv claude_hi_z hi_per_100g sugar_per_100g, by(module_code)
cap drop hi_q
xtile hi_q = claude_hi_z, n(4)

reg claude_hi_z eta_iv, r

* Main result: does income elasticity of demand predict module-level innovation?
reg ssnp eta_iv [aw=sqrt(spending)], r

* Heterogeneity: is the elasticity-innovation link stronger in healthy modules?
reg ssnp c.eta_iv##ib4.hi_q [aw=sqrt(spending)], robust



// ============================================================================
// JARAVEL IV -- FAILED 
// ============================================================================

// collapse to module
collapse (mean) ssnp d_spending spending iv_jaravel claude_hi_z, by(module_code)

cap drop hi_q
xtile hi_q = claude_hi_z, n(4)

* First stage
ivreghdfe d_spending iv_jaravel [aw=sqrt(spending)], cluster(module_code)

* IV: innovation on demand
ivreghdfe ssnp (d_spending = iv_jaravel) [aw=sqrt(spending)], cluster(module_code)

ivreghdfe ssnp (c.d_spendin#b4.hi_q = c.iv_jaravel#b4.hi_q) [aw=sqrt(spending)], cluster(module_code)


	
	
	
	
// national data defines new as first in country
// log_real_spending = log(nominal_spending) − log(price_level_ces) — the level of log real spending in module m, year t
// d_spending = first difference of log_real_spending within module (or module×county) — the growth rate, i.e. ≈ % change in real spending year-over-year-over-year

xtset module_code year 

// define forward diff
cap drop f_ssnp
gen f_ssnp = F.ssnp - ssnp

cap drop f_spend
gen f_spend = F.log_real_spending - log_real_spending

cap drop f_iv
gen f_iv = F.iv_bartik_bls - iv_bartik_bls


cap drop f5_ssnp
gen f5_ssnp = F5.ssnp - ssnp
cap drop f5_spend
gen f5_spend = F5.log_real_spending - log_real_spending
cap drop f5_iv
gen f5_iv = F5.iv_bartik_bls - iv_bartik_bls


// sai says am i use expenditure wieght or quantity (sales) weights 

// OLS version = .0086
reghdfejl ssnp log_real_spending [aw=spending], absorb(module_code year) cluster(module_code)

// first stage 
reghdfejl log_real_spending iv_bartik [aw=spending], absorb(module_code year) cluster(module_code)

reghdfejl log_real_spending iv_bartik_bls [aw=spending], absorb(module_code year) cluster(module_code)


cap drop hi_q
xtile hi_q = hi_per_100g, n(4)

// IV - Real spending panel version = .459
reghdfejl ssnp (log_real_spending = iv_bartik) [aw=spending], absorb(module_code year) cluster(module_code)

// IV - Expenditure growth version = .391
reghdfejl ssnp (d_spending = iv_bartik_bls) [aw=spending], absorb(module_code year) cluster(module_code)

// Heterogeneity by healthines
reghdfejl ssnp (c.d_spending#i.hi_q = c.iv_bartik_bls#i.hi_q) [aw=spending], absorb(module_code year) cluster(module_code)


// Heterogeneity by baseline level of variety 

// IV - First diff = .599
reghdfejl D.ssnp (D.log_real_spending = D.iv_bartik_bls) [aw=spending], absorb(module_code year) cluster(module_code)

// IV - Forward diff = ю487  
reghdfejl f_ssnp (D.d_spending = D.iv_bartik_bls) [aw=spending], absorb(module_code year) cluster(module_code)

// IV - Pre-trend = .520
reghdfejl D.ssnp (f_spend = f_iv) [aw=spending], absorb(module_code year) cluster(module_code)


// IV - Expenditure growth version = .391
reghdfejl n_new_upcs (d_spending = iv_bartik_bls) [aw=spending], absorb(module_code year) cluster(module_code)






// County data defines new as first in country  
destring fips, replace
xtset fips year 

//With the panel set on fips, Stata's D.log_real_spending would compute differences across years within fips, not within module. That would be wrong — you want the change in module-level real spending, not fips-level. Since log_real_spending_cty varies by (module, fips, year), the .diff() in Python groups by both (product_module_code, fips) to get the right within-module×county difference, then drops the level variable.

// first stage w old IV -- also super strong at county level 
reghdfejl d_spending iv_income [aw=spending], absorb(module_code fips year) cluster(module_code)
// first stage w new BLS IV -- super strong at county level 
reghdfejl d_spending bartik_bls [aw=spending], absorb(module_code fips year) cluster(module_code)


// 2SLS by county by code by year  = .104
reghdfejl ssnp (d_spending = bartik_bls) [aw=spending], absorb(module_code fips year) cluster(module_code)

// -35
reghdfejl n_new_upcs (d_spending = bartik_bls) [aw=spending], absorb(module_code fips year) cluster(module_code)

//
reghdfejl share_new_upcs (d_spending = bartik_bls) [aw=spending], absorb(module_code fips year) cluster(module_code)


// let's run it by the module level 
collapse (mean) ssnp d_spending bartik_bls spending n_new_upcs share_new_upcs, by(module_code year)

// this is very weak
reghdfejl ssnp (d_spending = bartik_bls) [aw=spending], absorb(module_code year) cluster(module_code)

// and that's because the first stage at the module level is very weak
// F = .37
reghdfejl d_spending bartik_bls [aw=spending], absorb(module_code year) cluster(module_code)




// BLS bartik 
use "$data/interim/panel_dataset/bartik_bls_module_iv.dta", clear
tempfile bls
save `bls'

use "$data/interim/panel_dataset/innovation_reg_data_county.dta", clear
merge m:1 module_code year using `bls', keepusing(bartik_bls) nogen


















