import delimited "/Users/alexandersax/Google Drive/Side Projects/lol_analysis/data/matches.csv", clear

// Get hour data
clonevar smatchcreation = matchcreation
replace smatchcreation = smatchcreation + msofhours(24)*3653 - msofhours(5)
format %tc smatchcreation
gen hour = hh(smatchcreation) - 2
replace hour  = hour + 24 if hour < 0
order smatchcreation hour, first

save "/Users/alexandersax/Google Drive/Side Projects/lol_analysis/data/matches.dta", replace

preserve
collapse winner, by(hour)
twoway bar winner hour
restore

// Check whether I play better/worse when warmed up
// Looks like I play better, but not stat sig
prtest winner, by(fastrequeue)


// Should I take a break after losing two in a row, or losing one?
// Turns out that hotstreaks are only confirmation bias
sort wonlastgame
by wonlastgame: tab winner if fastrequeue == 1
prtest winner if fastrequeue==1, by(wonlastgame)
// testing runs
sort matchcreation
runtest winner


probit winner wonlastgame if fastrequeue==1

