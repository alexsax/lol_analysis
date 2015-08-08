import delimited "/Users/alexandersax/Google Drive/Side Projects/lol_analysis/data/basic_stats.csv", clear

// Get hour data
clonevar smatchcreation = matchcreation
replace smatchcreation = smatchcreation + msofhours(24)*3653 - msofhours(5)
format %tc smatchcreation
gen hour = hh(smatchcreation) - 2
replace hour  = hour + 24 if hour < 0
order smatchcreation hour, first

preserve
collapse winner, by(hour)
twoway bar winner hour
restore
