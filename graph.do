import delimited "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/interim/census_merged_1992_2022_deflated.tsv", clear 

import delimited "/Users/anyamarchenko/CEGA Dropbox/Anya Marchenko/corn/raw/NASS_2017-2022/qs.census2017.txt", clear

*br if strpos(short_desc, "CONSERVATION") > 0 & agg_level_desc == "COUNTY" & domain_desc =="TOTAL" 

br if strpos(short_desc, "CORN") > 0 & agg_level_desc == "NATIONAL" & domain_desc =="TOTAL" 

*preserve


